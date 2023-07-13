import os

# Django Dependencies
from django.conf import settings
from django.shortcuts import render

# Application Modules
import core.data_loading.data_loading as log_import
from group_analysis.group_managment.group_managment_utils import (
    get_active_groups,
    check_group_managment,
    get_diag,

)

# Create your views here.


def group_analysis(request):
    event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
    log_information = None
    active_group_details = None
    diagnostics=None
    # TODO Running Example, on how to display Plot

    # Use this to include it in the UI

    # TODO Load the Log Information, else throw/redirect to Log Selection
    if "current_log" in request.session and request.session["current_log"] is not None:
        log_information = request.session["current_log"]
        print("Log Information: ", log_information)

    # TODO Get the Groups, from the Post
    if log_information is not None:

        event_log = os.path.join(event_logs_path, log_information["log_name"])

        log_format = log_import.get_log_format(log_information["log_name"])

        # Import the Log considering the given Format
        _, activities = log_import.log_import(event_log, log_format, log_information)

        # Set the activities to the activities of the loaded log.
        request.session["activities"] = list(activities)
        active_group_details = get_active_groups(request)
        diagnostics=get_diag(request)
        if diagnostics is None:
            diagnostics=''
        return render(
            request,
            "group_analysis.html",
            {
                "log_name": settings.EVENT_LOG_NAME,
                "active_group_details": active_group_details,
                "diagnostics":diagnostics,
            },
        )

    else:

        if check_group_managment(request):

            active_group_details = get_active_groups(request)
            diagnostics=get_diag(request)
            if diagnostics is None:
                diagnostics=''
        return render(
            request,
            "group_analysis.html",
            {"active_group_details": active_group_details,
                "diagnostics":diagnostics,
            },
        )
