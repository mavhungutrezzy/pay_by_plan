from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Layby(models.Model):
    """
    Represents a layby purchase, which allow customer to pay for items in installments.

    A layby purchase requires an initial deposit and regular payments until the total
    cost is paid off. The item is held by the shop until full payment is received.
    """

    FREQUENCY_BIWEEKLY = "biweekly"
    FREQUENCY_MONTHLY = "monthly"

    FREQUENCY_CHOICES = [
        (FREQUENCY_BIWEEKLY, _("Bi-weekly")),
        (FREQUENCY_MONTHLY, _("Monthly")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="laybys",
        verbose_name=_("User"),
    )
    shop_name = models.CharField(
        _("Shop name"),
        max_length=100,
        db_index=True,
    )
    item_description = models.TextField(
        _("Item description"),
    )
    total_cost = models.DecimalField(
        _("Total cost"),
        max_digits=10,
        decimal_places=2,
    )
    payment_frequency = models.CharField(
        _("Payment frequency"),
        max_length=10,
        choices=FREQUENCY_CHOICES,
        default=FREQUENCY_MONTHLY,
    )
    start_date = models.DateField(
        _("Start date"),
        default=timezone.now,
    )
    expected_end_date = models.DateField(
        _("Expected end date"),
    )
    is_active = models.BooleanField(
        _("Is active"),
        default=True,
        help_text=_("Indicates if the layby is currently active"),
    )
    is_complete = models.BooleanField(
        _("Is complete"),
        default=False,
        help_text=_("Indicates if all payments have been made"),
    )
    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("Updated at"),
        auto_now=True,
    )

    class Meta:
        verbose_name = _("Layby")
        verbose_name_plural = _("Laybys")
        ordering = ["-start_date"]
        indexes = [
            models.Index(fields=["-start_date", "user"]),
        ]

    def __str__(self):
        return f"{self.shop_name} - {self.item_description[:30]}"

    def clean(self):
        """Validate the model data."""

        if self.expected_end_date <= self.start_date:
            raise ValidationError(
                {"expected_end_date": _("Expected end date must be after start date")},
            )

    def remaining_balance(self) -> Decimal:
        """
        Calculate the remaining balance for this layby.

        Returns:
            Decimal: The amount still to be paid
        """
        paid_amount = sum(payment.amount for payment in self.payments.all())
        return self.total_cost - paid_amount

    def is_overdue(self) -> bool:
        """
        Check if the layby is overdue based on expected end date.

        Returns:
            bool: True if the layby is active, not complete, and past
            its expected end date
        """
        return (
            self.is_active
            and not self.is_complete
            and self.expected_end_date < timezone.now().date()
        )

    def get_total_payments(self) -> float:
        """
        Calculate the total amount of payments received for this layby.

        Returns:
            float: The total amount of payments
        """
        return self.payments.aggregate(total=models.Sum("amount"))["total"] or 0

    def mark_as_complete(self):
        """
        Mark the layby as complete or incomplete.

        Returns:
            None
        """
        if self.is_complete:
            self.is_complete = False
        else:
            self.is_complete = True

    def mark_as_active(self):
        """
        Mark the layby as active or inactive.

        Returns:
            None
        """
        if self.is_active:
            self.is_active = False
        else:
            self.is_active = True
