from dashboard.services import DashboardService
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View


class UserDashboardView(LoginRequiredMixin, View):

    login_url =  reverse_lazy("account_login")

    def get(self, request, *args, **kwargs):
        # Fetch dashboard data using the service
        dashboard_data = DashboardService.get_user_dashboard(request.user)

        # Pass the data to the template context
        context = {
            "dashboard_data": dashboard_data,
        }

        # Render the template with the context
        return render(request, "pages/home.html", context)
