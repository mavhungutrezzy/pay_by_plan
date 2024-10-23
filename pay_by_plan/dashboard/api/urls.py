from dashboard.api.views import DashboardViewSet
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

app_name = "dashboard"

router = DefaultRouter()
router.register("dashboard", DashboardViewSet, basename="dashboard")

urlpatterns = [
    path("", include(router.urls)),
]
