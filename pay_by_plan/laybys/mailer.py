from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import Layby


class LaybyMailer:
    """Handles all layby-related email notifications."""

    @classmethod
    def send_layby_confirmation(cls, layby: Layby) -> None:
        """
        Send email confirming the layby
        """
        context = {
            "user": layby.user,
            "layby": layby,
            "total_cost": layby.total_cost,
        }

        send_mail(
            subject="Your Layby Purchase Confirmation",
            message=render_to_string("laybys/emails/confirmation.txt", context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[layby.user.email],
        )
