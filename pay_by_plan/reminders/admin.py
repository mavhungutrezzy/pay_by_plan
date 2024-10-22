from django.contrib import admin
from reminders.services import NotificationService

from .models import Notification
from .models import Reminder


class NotificationInline(admin.TabularInline):
    model = Notification
    extra = 1
    readonly_fields = ("sent_at", "is_sent")
    can_delete = True
    fields = ("sent_at", "is_sent")


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = (
        "layby",
        "frequency",
        "next_reminder_date",
        "is_active",
        "has_notifications",
    )
    list_filter = ("frequency", "next_reminder_date", "is_active")
    search_fields = ("layby__shop_name", "layby__user__email")
    inlines = [NotificationInline]
    actions = ["send_reminder_notifications"]

    def has_notifications(self, obj):
        return obj.notifications.exists()

    has_notifications.short_description = "Has Notifications"

    def send_reminder_notifications(self, request, queryset):
        """
        Custom admin action to send reminders manually from the admin interface.
        """
        for reminder in queryset:
            NotificationService.send_reminder_notification(reminder)
        self.message_user(request, f"{queryset.count()} reminders processed.")

    send_reminder_notifications.short_description = "Send reminder notifications"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("reminder", "sent_at", "is_sent")
    list_filter = ("is_sent", "sent_at")
    search_fields = ("reminder__layby__shop_name", "reminder__layby__user__email")
    readonly_fields = ("sent_at", "is_sent")  # Remove 'reminder' from readonly_fields

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return (*self.readonly_fields, "reminder")
        return self.readonly_fields  # Creating a new object
