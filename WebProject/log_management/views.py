import os
import re
from datetime import timedelta as td
import random
import pandas as pd

from wsgiref.util import FileWrapper
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.conf import settings

from log_management.services.log_service import LogService
from core.models import SelectedLog
import core.data_loading.data_loading as log_import

import pm4py
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.algo.evaluation.replay_fitness import algorithm as replay_fitness

LOGMANAGEMENT_DIR = "log_management"
petrinet_path = os.path.join(settings.MEDIA_ROOT, "petrinets")
event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
log=None
aligned_traces=None
weighingtimedict={}


def index(request):
    """Returns the index views. Supports both GET and POST methods."""

    log_service = LogService()
    if request.method == "POST":
        if "uploadButton" in request.POST:
            print("here!")
            # check if the file is missing
            event_log_is_missing = "event_log" not in request.FILES
            if event_log_is_missing:
                return HttpResponseRedirect(request.path_info)

            log = request.FILES["event_log"]
            # Check if the file is valid
            # TODO: Perhaps move this logic inside LogService with an exception
            # being thrown
            isInvalidFile = re.search(".(xes|csv)$", log.name.lower()) is None
            if isInvalidFile:
                return HttpResponseRedirect(request.path_info)
            log_service.saveLog(log)
        elif "uploadpnButton" in request.POST:
            print("here!")
            # check if the file is missing
            petrinet_is_missing = "petrinet" not in request.FILES
            if petrinet_is_missing:
                return HttpResponseRedirect(request.path_info)

            petrinet = request.FILES["petrinet"]
            # Check if the file is valid
            # TODO: Perhaps move this logic inside LogService with an exception
            # being thrown
            selected_petrinet = petrinet.name
            request.session["current_net"] = selected_petrinet
            log_service.savePetrinet(petrinet)
        elif "deleteButton" in request.POST:
            if "log_list" not in request.POST:
                return HttpResponseRedirect(request.path_info)
            logname = request.POST["log_list"]
            log_service.deleteLog(logname)
        elif "downloadButton" in request.POST:
            if "log_list" not in request.POST:
                return HttpResponseRedirect(request.path_info)

            filename = request.POST["log_list"]
            file_dir = log_service.getLogFile(filename)

            try:
                wrapper = FileWrapper(open(file_dir, "rb"))
                response = HttpResponse(
                    wrapper, content_type="application/force-download"
                )
                response[
                    "Content-Disposition"
                ] = "inline; filename=" + os.path.basename(file_dir)
                return response
            except Exception as e:
                return None
        elif "setButton" in request.POST:
            if "log_list" not in request.POST:
                return HttpResponseRedirect(request.path_info)
            filename = request.POST["log_list"]

            return redirect("setlog/" + filename + "/")

    eventlog_list = log_service.getAll()
    my_dict = {"eventlog_list": eventlog_list}

    if "current_log" in request.session and request.session["current_log"] is not None:
        try:
            my_dict["selected_log_info"] = request.session["current_log"]
        except Exception as err:
            print("Oops!  Fetching the log failed: {0}".format(err))
    if "current_net" in request.session and request.session["current_net"] is not None:
        if "fitness" in request.session and request.session["fitness"] is not None:
            my_dict["fitness"]=request.session["fitness"]
        try:
            my_dict["selected_petrinet_info"] = request.session["current_net"]
        except Exception as err:
            print("Oops!  Fetching the petrinet failed: {0}".format(err))
    if "fitness" not in request.session:
        try:
            fitness=check_fitness(request)
            my_dict["fitness"] = request.session["fitness"]
        except Exception as err:
            print("Oops!  Fetching the petrinet failed: {0}".format(err))

    return render(request, LOGMANAGEMENT_DIR + "/index.html", context=my_dict)

def check_fitness(request):
    global log
    global aligned_traces
    net, initial_marking, final_marking = pnml_importer.apply(os.path.join(petrinet_path,request.session["current_net"]) )
    log_information = request.session["current_log"]
    event_log = os.path.join(event_logs_path, log_information["log_name"])
    log_format = log_import.get_log_format(log_information["log_name"])
    log, activities = log_import.log_import(event_log, log_format, log_information)
    aligned_traces = pm4py.conformance_diagnostics_alignments(log, net, initial_marking, final_marking)
    request.session["fitness"]=replay_fitness.evaluate(aligned_traces, variant=replay_fitness.Variants.ALIGNMENT_BASED)
    return request.session["fitness"]


def set_log(request, logname):
    """Sets the specified log as current using session memory"""
    log_service = LogService()

    if request.method == "POST":
        name = request.POST["logName"]
        case_id = request.POST["caseId"]
        concept_name = request.POST["caseConcept"]

        selected_log = SelectedLog(name, case_id, concept_name)

        selected_log.log_type = request.POST["inlineRadioOptions"]
        if selected_log.log_type == "noninterval":
            selected_log.timestamp = request.POST["timestamp"]
        elif selected_log.log_type == "lifecycle":
            selected_log.lifecycle = request.POST["lifecycle"]
            selected_log.timestamp = request.POST["timestamp"]
        elif selected_log.log_type == "timestamp":
            selected_log.start_timestamp = request.POST["startTimestamp"]
            selected_log.end_timestamp = request.POST["endTimestamp"]

        request.session["current_log"] = selected_log.__dict__

        # (Re)Initialize Group and Activities
        request.session["activities"] = None
        request.session["group_details"] = None

        return redirect("/logmanagement/")

    data = log_service.getLogInfo(logname).__dict__
    return render(request, LOGMANAGEMENT_DIR + "/set_log.html", context=data)


def get_log_info(request):
    """Returns information about a log. WIP"""
    log_service = LogService()

    log_name = request.GET.get("log_name", None)

    data = log_service.getLogInfo(log_name).__dict__
    print(data)
    html = loader.render_to_string(LOGMANAGEMENT_DIR + "/log_info.html", data)
    # print(html)
    return HttpResponse(html)


def get_new_fitness(request):
    """Returns information about a log. WIP"""
    fitness=check_fitness(request)
    html = loader.render_to_string(LOGMANAGEMENT_DIR + "/fitness.html", fitness)
    # print(html)
    return HttpResponse(html)

def fit(request):
    iter=0
    index=1
    net, initial_marking, final_marking = pnml_importer.apply(os.path.join(petrinet_path,request.session["current_net"]) )
    log_information = request.session["current_log"]
    event_log = os.path.join(event_logs_path, log_information["log_name"])
    log_format = log_import.get_log_format(log_information["log_name"])
    log, activities = log_import.log_import(event_log, log_format, log_information)
    aligned_traces = pm4py.conformance_diagnostics_alignments(log, net, initial_marking, final_marking)
    log_service = LogService()
    for trace,login in zip(aligned_traces,log):
        iter=0
        index=index+1
        if trace['fitness']<1:
            for item in trace['alignment']:
                #move on model- adding an activity
                if (item[0]!=item[1]) and item[0]=='>>' and item[1] is not None:
                    print('adding:',item[1])
                    newitem=lastitem.__copy__()
                    print(len(login))
                    if len(login)<iter:
                        nextitemtime=login.__getitem__(iter).__getitem__('time:timestamp')
                    else :
                        nextitemtime=0
                    newitem.__setitem__('concept:name',item[1])
                    time=lastitem.__getitem__('time:timestamp')
                    weightingtime=random.choices(listweightingtime(log,item[1]))[0]
                    print(weightingtime)
                    if nextitemtime==0 or nextitemtime-time>weightingtime:
                        newitem.__setitem__('time:timestamp',time+weightingtime)
                    else :
                        print("here:",(nextitemtime-time)/2)
                        newitem.__setitem__('time:timestamp',time+(nextitemtime-time)/2)
                    login.insert(iter,newitem)
                    iter=iter+1
                #move on log- deleting an activity
                elif (item[0]!=item[1]) and item[1]=='>>' and item[0] is not None:
                    print('deleting',item[0],"-",iter)
                    login.__getitem__(iter).__setitem__('concept:name','readytodelete')
                    #login.__setitem__(iter,None)
                    #print(login)
                if item[0]!='>>' and item[0]!='readytodelete' and item[0] is not None:
                    lastitem=login.__getitem__(iter)
                    iter=iter+1
    log = pm4py.filter_event_attribute_values(log, "concept:name", ["readytodelete"], level="event", retain=False)
    pm4py.write_xes(log, event_logs_path+'/fitted.xes')
    return get_new_fitness(request)

def listweightingtime(log, event):
    if event in weighingtimedict:
        return weighingtimedict[event]
    waitingtime=[]
    for case in log:
        time=None
        lasttime=None
        for events in case:
            if events['concept:name']==event:
                time=events['time:timestamp']
                break
            else :
                lasttime=events['time:timestamp']
        if time is not None and lasttime is not None:
            waitingtime.append(pd.to_datetime(time, utc=True)-pd.to_datetime(lasttime, utc=True))
    weighingtimedict[event]=waitingtime
    return waitingtime