from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from laybys.models import Layby


class Payment(models.Model):
    """Represents a payment made towards a layby."""

    layby = models.ForeignKey(
        Layby,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("Layby"),
    )
    amount = models.DecimalField(
        _("Amount"),
        max_digits=10,
        decimal_places=2,
    )
    payment_date = models.DateTimeField(
        _("Payment date"),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        ordering = ["-payment_date"]

    def __str__(self):
        return f"{self.layby} - ${self.amount} on {self.payment_date.date()}"

    def clean(self):
        if self.amount <= 0:
            raise ValidationError(_("Payment amount must be a positive number."))

        if self.amount > self.layby.total_cost - self.layby.get_total_payments():
            raise ValidationError(
                _("Payment amount exceeds the remaining balance of the layby."),
            )

        if self.layby.is_complete:
            raise ValidationError(
                _("Layby is already complete. No further payments can be made."),
            )

        if not self.layby.is_active:
            raise ValidationError(_("Layby is inactive. Payments cannot be made."))
