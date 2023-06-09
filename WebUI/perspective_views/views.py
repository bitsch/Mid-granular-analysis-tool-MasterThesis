import re
import os
import json
from django.http.response import JsonResponse, HttpResponse
from django.template import loader


from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
import pm4py

# Django Dependencies
from django.shortcuts import render
from django.conf import settings

# Application Modules
import perspective_views.plotting.plot_creation as plotting
import perspective_views.retrieval.statistics as stats
import core.data_loading.data_loading as log_import


# Create your views here.


def perspective(request):
    event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
    load_log_succes = False
    log_information = None

    # TODO Load the Log Information, else throw/redirect to Log Selection
    if "current_log" in request.session and request.session["current_log"] is not None:
        log_information = request.session["current_log"]
        print(log_information)

    if log_information is not None:

        event_log = os.path.join(event_logs_path, log_information["log_name"])
        log_format = log_import.get_log_format(log_information["log_name"])

        # Import the Log considering the given Format
        log, activities = log_import.log_import(event_log, log_format, log_information)
        load_log_succes = True

    if request.method == "POST":
        # TODO Throw some error
        print("Not yet implemented")

    else:

        if load_log_succes:
            result = stats.get_log_statistics(log, log_format, log_information)
            dfg = dfg_discovery.apply(log)
            this_data, temp_file = plotting.dfg_to_g6(dfg)
            re.escape(temp_file)
            result["Nunique_Activities"] = len(activities)
            return render(
                request,
                "perspective_view.html",
                {
                    "log_name": settings.EVENT_LOG_NAME,
                    "json_file": temp_file,
                    "data": json.dumps(this_data),
                    "activities": activities,
                    "result": result,
                },
            )

        else:
            return render(request, "perspective_view.html")


def activity_filter(request):
    event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
    load_log_succes = False
    log_information = None
    filteredresult = None
    # TODO Load the Log Information, else throw/redirect to Log Selection
    if "current_log" in request.session and request.session["current_log"] is not None:
        log_information = request.session["current_log"]
        print(log_information)

    if log_information is not None:

        event_log = os.path.join(event_logs_path, log_information["log_name"])
        log_format = log_import.get_log_format(log_information["log_name"])

        # Import the Log considering the given Format
        log, activities = log_import.log_import(event_log, log_format, log_information)
        load_log_succes = True

    if request.method == "POST":
        selected_activity = request.POST["selected_activity"]
        result = stats.get_log_statistics(log, log_format, log_information)
        case_ids = stats.get_case_ids_by_activity(
            log, selected_activity, log_format, log_information
        )


        
        if log_format == "xes": 
            filtered_log = pm4py.filter_trace_attribute_values(
                log, log_information["case_id"], case_ids, retain=True)
        else: 
            filtered_log = log[log["case:concept:name"].isin(case_ids)]




        filteredresult = stats.get_log_statistics(
            filtered_log, log_format, log_information
        )
        
        dfg = dfg_discovery.apply(filtered_log)
        this_data, temp_file = plotting.dfg_to_g6(dfg)
        re.escape(temp_file)
        network = {}
        if filteredresult is None:
            filteredresult = result
        keys_to_extract = [
            "Nvariant",
            "Nunique_Activities",
            "Nactivities",
            "Ncase",
            "StartTime",
            "EndTime",
            "TotalDuration",
            "MedianCaseDuration",
            "MeanCaseDuration",
            "MinCaseDuration",
            "MaxCaseDuration",
        ]
        subsetfilteredresult = {
            key: str(filteredresult[key]) for key in keys_to_extract
        }

    message = {
        "success": True,
        "filtered_result": subsetfilteredresult,
        "data": json.dumps(this_data),
        "responseText": "Inactivated successfully!",
    }
    return JsonResponse(message)


def case_filter_dfg(request):
    event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
    log_information = None
    # TODO Load the Log Information, else throw/redirect to Log Selection
    if "current_log" in request.session and request.session["current_log"] is not None:
        log_information = request.session["current_log"]
        print(log_information)

    if log_information is not None:

        event_log = os.path.join(event_logs_path, log_information["log_name"])
        log_format = log_import.get_log_format(log_information["log_name"])

        # Import the Log considering the given Format
        log, activities = log_import.log_import(event_log, log_format, log_information)

    if request.method == "POST":
        selected_case = request.POST["selected_case"]
       
        if log_format == "xes": 
            filtered_log = pm4py.filter_trace_attribute_values(
                log, log_information["case_id"], [selected_case], retain=True)
        else: 
            filtered_log = log[log["case:concept:name"].isin([selected_case])]

        dfg = dfg_discovery.apply(filtered_log)
        this_data, temp_file = plotting.dfg_to_g6(dfg)
        re.escape(temp_file)
    message = {
        "success": True,
        "data": json.dumps(this_data),
        "responseText": "Inactivated successfully!",
    }
    return JsonResponse(message)


def case_filter_plt(request):

    event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
    log_information = None
    # TODO Load the Log Information, else throw/redirect to Log Selection
    if "current_log" in request.session and request.session["current_log"] is not None:
        log_information = request.session["current_log"]

    if log_information is not None:

        event_log = os.path.join(event_logs_path, log_information["log_name"])
        log_format = log_import.get_log_format(log_information["log_name"])

        # Import the Log considering the given Format
        log, activities = log_import.log_import(event_log, log_format, log_information)

    if request.method == "POST":
        selected_case = request.POST["selected_case"]
        df = plotting.create_df_case(log, log_format, [selected_case], log_information)

        plot_div = plotting.timeframe_plot(df)
        html = loader.render_to_string("view_plot.html", {"plot_div": plot_div})
        return HttpResponse(html)

    else:
        print("DEBUG: POST URL REQUESTED!")


def change_view(request):
    if request.method == "POST":
        selected_view = request.POST["selected_view"]
    message = {"success": True, "responseText": "Inactivated successfully!"}
    return JsonResponse(message)
