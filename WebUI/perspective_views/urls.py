from django.conf.urls import url
from django.urls import path

from perspective_views import views

urlpatterns = [
    # path("", views.perspective, name="perspective"),
    url(r"^$", views.perspective, name="perspective"),
    url(
        r"^ajax/activityfilter/$",
        views.activity_filter,
        name="activity_filter",
    ),
    url(
        r"^ajax/changeView/$",
        views.change_view,
        name="change_view",
    ),
    url(
        r"^ajax/casefilter/dfg$",
        views.case_filter_dfg,
        name="case_filter_dfg",
    ),
    url(
        r"^ajax/casefilter/plt$",
        views.case_filter_plt,
        name="case_filter_plt",
    ),
]
