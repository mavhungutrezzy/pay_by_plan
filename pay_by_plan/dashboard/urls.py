from django.urls import path

from .views import UserDashboardView

urlpatterns = [
    path("", UserDashboardView.as_view(), name="user-dashboard"),
]
