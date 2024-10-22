from reminders.models import Notification
from reminders.models import Reminder
from rest_framework import serializers


class ReminderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ["layby", "frequency", "next_reminder_date"]


class ReminderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ["frequency", "next_reminder_date", "is_active"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "sent_at", "is_sent"]


class ReminderSerializer(serializers.ModelSerializer):
    notifications_count = serializers.SerializerMethodField()

    class Meta:
        model = Reminder
        fields = [
            "id",
            "layby",
            "frequency",
            "next_reminder_date",
            "is_active",
            "notifications_count",
        ]

    def get_notifications_count(self, obj):
        return obj.notifications.count()
