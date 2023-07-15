from django.urls import path
from . import views

app_name = 'matchingconfig'

urlpatterns = [
    path("", views.matchconfiguration,
         name="match-config"),  # New url 'matchingconfig' added
]
