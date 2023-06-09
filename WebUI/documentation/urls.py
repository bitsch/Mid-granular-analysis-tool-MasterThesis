from django.conf.urls import url
from documentation import views

urlpatterns = [
    url(r"^$", views.index, name="documentation-index"),
]
