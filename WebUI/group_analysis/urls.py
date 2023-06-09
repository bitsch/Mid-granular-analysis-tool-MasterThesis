from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path("", views.group_analysis, name="group_analysis"),
]
