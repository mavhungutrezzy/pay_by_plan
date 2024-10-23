from django.utils import timezone
from drf_spectacular.utils import extend_schema
from reminders.models import Notification
from reminders.models import Reminder
from reminders.tasks import process_reminders_manual
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import NotificationSerializer
from .serializers import ReminderCreateSerializer
from .serializers import ReminderSerializer
from .serializers import ReminderUpdateSerializer


@extend_schema(tags=["reminders"])
class ReminderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reminders and notifications.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter reminders based on user's laybys
        return Reminder.objects.filter(layby__user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return ReminderCreateSerializer
        if self.action in ["update", "partial_update"]:
            return ReminderUpdateSerializer
        return ReminderSerializer

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """Toggle reminder active status."""
        reminder = self.get_object()
        reminder.is_active = not reminder.is_active
        reminder.save()
        return Response({"status": "success", "is_active": reminder.is_active})

    @action(detail=True, methods=["get"])
    def notification_history(self, request, pk=None):
        """Get notification history for a specific reminder."""
        reminder = self.get_object()
        notifications = reminder.notifications.order_by("-sent_at")
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """Get upcoming reminders for the next 7 days."""
        end_date = timezone.now().date() + timezone.timedelta(days=7)
        reminders = (
            self.get_queryset()
            .filter(next_reminder_date__lte=end_date, is_active=True)
            .order_by("next_reminder_date")
        )
        serializer = self.get_serializer(reminders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def process_due_reminders(self, request):
        """Manually trigger reminder processing."""
        process_reminders_manual()
        return Response(
            {"status": "Due reminders scheduled for processing"},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["post"])
    def send_now(self, request, pk=None):
        """Immediately send a reminder regardless of schedule."""
        self.get_object()
        try:
            process_reminders_manual()
            return Response({"status": "Reminder sent successfully"})
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def reset_schedule(self, request, pk=None):
        """Reset the reminder schedule to start from today."""
        reminder = self.get_object()
        reminder.next_reminder_date = timezone.now().date()
        reminder.save()
        return Response({"next_reminder_date": reminder.next_reminder_date})


@extend_schema(tags=["notifications"])
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing notification history.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(
            reminder__layby__user=self.request.user,
        ).order_by("-sent_at")

    @action(detail=False, methods=["get"])
    def recent(self, request):
        """Get recent notifications (last 30 days)."""
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        notifications = self.get_queryset().filter(sent_at__gte=thirty_days_ago)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
