import os
import time
# Django Dependencies
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.conf import settings

# Core
import core.data_loading.data_loading as log_import

# Group Analysis
from group_analysis.group_managment.group_managment_utils import get_active_groups
import group_analysis.plotting.data_frame_creation as plotting_data
import group_analysis.plotting.plot_creation as plotting
from group_analysis.group_managment.group import Group

from pm4py.objects.petri_net.importer import importer as pnml_importer
# Application Modules

from pm4py.algo.conformance.tokenreplay import algorithm as token_replay

petrinet_path = os.path.join(settings.MEDIA_ROOT, "petrinets")
# Create your views here.
diag=[]
preddf=None
targetdf=None


def group_management(request):
    active_groups = None
    activities = None

    # Export this into a general function checking existance of the values
    # in the session,for activities, we might assume this
    # But better be safe than sorry
    if "places" in request.session:
        places = request.session["places"]
    else :
        places=get_places(request)
    if "group_details" in request.session:
        active_groups = get_active_groups(request)

    context = {"places": places, "active_group_details": active_groups}

    return render(request, "create_group_view.html", context)

def get_places(request):
    net, initial_marking, final_marking = pnml_importer.apply(os.path.join(petrinet_path,request.session["current_net"]) )
    return net.places


def save_group_info(request):
    if request.method == "POST":
        if "create_new_group" in request.POST:
            print(dict(request.POST.items()))
        group_name = request.POST["group_name"]
        selected_activities = request.POST["selected_activities"]
        data = {}
        data[group_name] = {
            "group_name": group_name,
            "selected_activities": selected_activities,
            "status": "active",
        }
        if (
            "group_details" in request.session
            and request.session["group_details"] is not None
        ):
            saved_dict = request.session["group_details"]
            saved_dict.update(data)
            request.session["group_details"] = saved_dict
        else:
            request.session["group_details"] = data
    message = {"success": True, "responseText": "Saved successfully!"}

    return JsonResponse(message)


def change_group_status(request):
    if request.method == "POST":
        group_name = request.POST["group_name"]
        existing_groups = request.session["group_details"]
        for key, value in existing_groups.items():
            if key == group_name and existing_groups[key]["status"] == "active":
                request.session["group_details"][key]["status"] = "inactive"
                request.session.save()
    message = {"success": True, "responseText": "Inactivated successfully!"}
    print(request.POST)
    return JsonResponse(message)

def cohort_analysis_data(request):
    global preddf
    global targetdf
    global diag
    diag=[]
    if request.method == "POST":
        event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
        post_data = dict(request.POST.lists())

        log_information = request.session["current_log"]

        event_log = os.path.join(event_logs_path, log_information["log_name"])
        log_format = log_import.get_log_format(log_information["log_name"])

        # Loading Group details
        group_details = request.session["group_details"]
        print(group_details)
        # Loading the Log
        log, activities = log_import.log_import(event_log, log_format, log_information)
        net, initial_marking, final_marking = pnml_importer.apply(os.path.join(petrinet_path,request.session["current_net"]) )
        replayed_traces = token_replay.apply(log, net, initial_marking, final_marking)
        # Consider Pickeling the Data for a quick performance boost after the first load
        if "predictor_zone" in request.POST:
            predictor_zone = Group(
                    group_details[request.POST["predictor_zone"]]["group_name"],
                    group_details[request.POST["predictor_zone"]][
                        "selected_activities"
                    ].split(", "),
                )
            print(predictor_zone.members)
            preddf = plotting_data.create_analysis_dataframe(log, net, replayed_traces, predictor_zone,log_information)
            diag=getdata(preddf,"predictor")
        if "target_zone" in request.POST:
            target_zone = Group(
                            group_details[request.POST["target_zone"]]["group_name"],
                            group_details[request.POST["target_zone"]][
                                "selected_activities"
                            ].split(", "),
                        )
            time.sleep(1)
            print(target_zone.members)
            targetdf = plotting_data.create_analysis_dataframe(log, net, replayed_traces, target_zone,log_information)
            diag=getdata(targetdf,"target")
            request.session["diagnostics"]=diag
            request.session.save()
            print(request.session["diagnostics"])
    message = {"success": True, "responseText": "Inactivated successfully!"}

    return JsonResponse(message)

def getdata(df,zone):
    global diag
    anomalies=0
    featurecount=0
    featurelist=['tokenproduced', 'tokenconsumed', 'tokenleft','oneframetoken', 'Count', 'AverageTimeSpent']
    for feature in featurelist:
        anomalies=anomalies+len(df[df['Strange_'+feature]==1].axes[0])
        if len(df[df['Strange_'+feature]==1].axes[0])>0:
            featurecount=featurecount+1
    if anomalies>0:
        message="There are "+str(anomalies)+" instance of anomalies in "+str(featurecount)+"  features of the dataset for the "+zone+" zone"
        diag.append(message)

    batches=(len(df[df['drift']>0]))
    if batches>0:
        message="There are "+str(batches)+" instance of changes in behavior in multiple features in the dataset for the "+zone+" zone"
        diag.append(message)
    return diag

def predict(request):
    global preddf
    global targetdf
    if request.method == "POST":
        print(targetdf)
        print(preddf)
        result=plotting.make_prediction(preddf,targetdf)
        diag.extend(result)

        request.session["diagnostics"]=diag
        request.session.save()
        print(request.session["diagnostics"])
    message = {"success": True, "responseText": "Inactivated successfully!"}
    print(request.POST)

    return JsonResponse(message)

def setparam(request):
    if "sensitivity" in request.POST:
        plotting_data.set_sensitivity(request.POST["sensitivity"])
    if "timeframe" in request.POST:
        plotting_data.set_timeframe(request.POST["timeframe"])
    message = {"success": True, "responseText": "Inactivated successfully!"}
    print(request.POST)

    return JsonResponse(message)
