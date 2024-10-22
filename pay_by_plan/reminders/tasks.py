from huey import crontab
from huey.contrib.djhuey import periodic_task
from huey.contrib.djhuey import task

from .services import ReminderService


@periodic_task(crontab(minute="0", hour="0"))  # Run daily at midnight
def process_due_reminders():
    ReminderService.process_due_reminders()


@task()
def process_reminders_manual():
    ReminderService.process_due_reminders()
