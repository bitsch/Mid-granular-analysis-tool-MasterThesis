import os

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

# Application Modules

# Create your views here.


def group_management(request):
    active_groups = None
    activities = None

    # Export this into a general function checking existance of the values
    # in the session,for activities, we might assume this
    # But better be safe than sorry
    if "activities" in request.session:
        activities = request.session["activities"]

    if "group_details" in request.session:
        active_groups = get_active_groups(request)

    context = {"activities": activities, "active_group_details": active_groups}

    return render(request, "create_group_view.html", context)


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

    if request.method == "POST":
        event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
        post_data = dict(request.POST.lists())

        log_information = request.session["current_log"]

        event_log = os.path.join(event_logs_path, log_information["log_name"])
        log_format = log_import.get_log_format(log_information["log_name"])

        # Loading Group details
        group_details = request.session["group_details"]

        # Loading the Log
        log, activities = log_import.log_import(event_log, log_format, log_information)

        # Creating the Plotting Data
        df = plotting_data.create_plotting_data(log, log_format, log_information)

        # Consider Pickeling the Data for a quick performance boost after the first load

        if request.POST["operation_type"] == "timeframe":

            # TODO Replace this with the Interval picker values covered by the UI
            start_time, end_time = tuple(request.POST["start_end_time"].split(" - "))

            group = Group(
                group_details[request.POST["selected_group_name"]]["group_name"],
                group_details[request.POST["selected_group_name"]][
                    "selected_activities"
                ].split(", "),
            )

            df = plotting_data.create_timeframe_dataframe(
                df, group, start_time, end_time
            )
            plot_div = plotting.timeframe_plot_factory(df)

        else:

            Groups = [
                Group(
                    group_details[name]["group_name"],
                    group_details[name]["selected_activities"].split(", "),
                )
                for name in group_details.keys()
                if name in post_data["selected_group_names[]"]
            ]
            freq = request.POST["selected_time"]
            date_frame = plotting_data.create_concurrency_frame(df, Groups)
            if request.POST["plot_type"] == "standard":

                plot_div = plotting.concurrency_plot_factory(
                    date_frame,
                    Groups,
                    freq=freq,
                    aggregate=settings.AGGREGATE_FUNCTIONS[
                        request.POST["selected_aggregation"]
                    ],
                )

            else:
                uniform = (
                    True if request.POST["amplitude_plot_type"] == "uniform" else False
                )
                plot_div = plotting.amplitude_plot_factory(date_frame, Groups, uniform)

    post_data["plot_div"] = plot_div

    html = loader.render_to_string("cohort_analysis_plot.html", post_data)
    print("Finished Plot Creation")

    return HttpResponse(html)
