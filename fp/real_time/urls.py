from django.urls import path,include
from . import views


app_name = "real_time"

urlpatterns = [
    path("", views.line_chart, name="real_time_page"),
]