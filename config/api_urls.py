from django.urls import include
from django.urls import path

app_name = "api"

urlpatterns = [
    path("", include("laybys.api.urls")),
    path("", include("payments.api.urls")),
    path("", include("dashboard.api.urls")),
    path("", include("reminders.api.urls")),
]
