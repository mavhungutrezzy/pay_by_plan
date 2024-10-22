from dashboard.services import DashboardService
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


class UserDashboardViewSet(ViewSet):
    def list(self, request):
        dashboard_data = DashboardService.get_user_dashboard(request.user)
        return Response(dashboard_data)
