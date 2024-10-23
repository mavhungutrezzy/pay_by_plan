from dashboard.services import DashboardService
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import DashboardOverviewSerializer


@extend_schema_view(
    overview=extend_schema(
        summary="Get dashboard overview",
        responses={200: DashboardOverviewSerializer},
    ),
    statistics=extend_schema(
        summary="Get dashboard statistics",
        responses={200: OpenApiTypes.OBJECT},
    ),
)
@extend_schema(tags=["dashboard"])
class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def overview(self, request):
        """
        Get comprehensive dashboard data including laybys, payments, and reminders.
        """
        dashboard_data = DashboardService.get_user_dashboard_overview(request.user)
        return Response(dashboard_data)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """
        Get statistical data for charts and graphs.
        """
        stats = DashboardService.get_user_statistics(request.user)
        return Response(stats)
