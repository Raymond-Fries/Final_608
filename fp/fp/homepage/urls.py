from django.urls import path
from . import views
from .views import Home

app_name = "homepage"

urlpatterns = [
    path('',Home.as_view(),name='homepage'),

]
