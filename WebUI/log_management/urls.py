from django.conf.urls import url
from log_management import views

urlpatterns = [
    url(r"^$", views.index, name="index"),
    url(r"^setlog/([a-zA-Z0-9._ -]+)/$", views.set_log, name="set_log"),
    url(r"^ajax/loginfo/$", views.get_log_info, name="get_log_info"),
]
