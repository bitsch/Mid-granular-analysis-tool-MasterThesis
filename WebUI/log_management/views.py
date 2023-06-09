import os
import re

from wsgiref.util import FileWrapper
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from log_management.services.log_service import LogService
from core.models import SelectedLog

LOGMANAGEMENT_DIR = "log_management"


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
    return render(request, LOGMANAGEMENT_DIR + "/index.html", context=my_dict)


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
