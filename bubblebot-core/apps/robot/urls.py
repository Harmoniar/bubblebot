from django.urls import path
from . import api


urlpatterns = [
    path("api/health/report", api.health_report, name="robot_health_report"),
    path("api/db/curdapi", api.curd_api, name="robot_db_curdapi"),
]
