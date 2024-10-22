from django.db import models
from django.utils.translation import gettext_lazy as _
from laybys.models import Layby


class Reminder(models.Model):
    FREQUENCY_CHOICES = [
        ("daily", _("Daily")),
        ("weekly", _("Weekly")),
        ("biweekly", _("Bi-weekly")),
        ("monthly", _("Monthly")),
    ]

    layby = models.OneToOneField(
        Layby,
        on_delete=models.CASCADE,
        related_name="reminder",
        verbose_name=_("Layby"),
    )
    frequency = models.CharField(
        _("Frequency"),
        max_length=10,
        choices=FREQUENCY_CHOICES,
    )
    next_reminder_date = models.DateField(_("Next reminder date"))
    is_active = models.BooleanField(_("Is active"), default=True)

    class Meta:
        verbose_name = _("Reminder")
        verbose_name_plural = _("Reminders")

    def __str__(self):
        return f"Reminder for {self.layby} - {self.get_frequency_display()}"

    @property
    def notifications(self):
        return self.notification_set.all()


class Notification(models.Model):
    reminder = models.ForeignKey(
        Reminder,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    sent_at = models.DateTimeField(_("Sent At"), auto_now_add=True)
    is_sent = models.BooleanField(_("Is Sent"), default=False)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    def __str__(self):
        return f"Email notification for {self.reminder}"
