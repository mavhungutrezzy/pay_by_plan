from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class ReminderMailer:
    @staticmethod
    def send_layby_reminder(user, layby):
        subject = "Reminder for Your Layby Payment"
        html_content = render_to_string(
            "reminders/layby_reminder.html",
            {"user": user, "layby": layby},
        )
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
