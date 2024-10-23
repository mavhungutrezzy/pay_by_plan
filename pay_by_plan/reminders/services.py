import logging
from smtplib import SMTPException

from django.utils import timezone

from .mailer import ReminderMailer
from .models import Notification
from .models import Reminder

logger = logging.getLogger(__name__)


class ReminderService:
    @staticmethod
    def get_due_reminders():
        return Reminder.objects.filter(
            next_reminder_date=timezone.now().date(),
            is_active=True,
        )

    @staticmethod
    def update_next_reminder_date(reminder):
        if reminder.frequency == "daily":
            reminder.next_reminder_date += timezone.timedelta(days=1)
        elif reminder.frequency == "weekly":
            reminder.next_reminder_date += timezone.timedelta(weeks=1)
        elif reminder.frequency == "biweekly":
            reminder.next_reminder_date += timezone.timedelta(weeks=2)
        elif reminder.frequency == "monthly":
            reminder.next_reminder_date += timezone.timedelta(days=30)
        reminder.save()

    @staticmethod
    def process_due_reminders():
        due_reminders = ReminderService.get_due_reminders()
        for reminder in due_reminders:
            NotificationService.send_reminder_notification(reminder)
            ReminderService.update_next_reminder_date(reminder)


class NotificationService:
    @staticmethod
    def create_notification(reminder: Reminder) -> Notification:
        return Notification.objects.create(reminder=reminder)

    @staticmethod
    def send_reminder_notification(reminder: Reminder):
        notification = NotificationService.create_notification(reminder)

        try:
            ReminderMailer.send_layby_reminder(reminder.layby.user, reminder.layby)
            NotificationService._update_notification(notification)
            logger.info(
                f"Successfully sent email notification for reminder {reminder.id}",
            )
        except SMTPException as e:
            logger.exception(
                f"Error sending email notification for reminder {reminder.id}: {e}",
            )
