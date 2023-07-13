from django.conf.urls import url

from group_management_views import views

urlpatterns = [
    # path('', views.create_group, name='create_group')
    url(r"^$", views.group_management, name="group_management"),
    url(
        r"^ajax/savegroupinfo/$",
        views.save_group_info,
        name="save_group_info",
    ),
    url(
        r"^ajax/changegroupstatus/$",
        views.change_group_status,
        name="change_group_status",
    ),
    url(
        r"^ajax/cohortanalysisdata/$",
        views.cohort_analysis_data,
        name="cohort_analysis_data",
    ),
    url(
            r"^ajax/predict/$",
            views.predict,
            name="predict",
        ),
    url(
        r"^ajax/setparam/$",
        views.setparam,
        name="setparam",
        ),
]
