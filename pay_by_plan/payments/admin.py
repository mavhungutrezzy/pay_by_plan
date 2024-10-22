from decimal import Decimal

from django.contrib import admin
from django.contrib import messages
from django.db.models import Sum
from django.utils.html import format_html
from laybys.models import Layby

from .models import Payment


class LaybyInline(admin.StackedInline):
    model = Layby
    extra = 0
    readonly_fields = (
        "shop_name",
        "item_description",
        "total_cost",
        "expected_end_date",
        "is_active",
        "is_complete",
    )
    can_delete = False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "layby",
        "user_name",
        "amount",
        "payment_date_formatted",
        "layby_shop_name",
    )
    list_filter = ("payment_date", "layby__shop_name")
    search_fields = (
        "layby__shop_name",
        "layby__user__username",
        "layby__user__email",
    )
    readonly_fields = ("layby_details",)
    date_hierarchy = "payment_date"

    def user_name(self, obj):
        return obj.layby.user.get_full_name()

    user_name.short_description = "User"

    def layby_shop_name(self, obj):
        return obj.layby.shop_name

    layby_shop_name.short_description = "Shop Name"

    def payment_date_formatted(self, obj):
        return obj.payment_date.strftime("%Y-%m-%d")

    payment_date_formatted.short_description = "Payment Date"

    def layby_details(self, obj):
        """
        Display relevant layby information in the payment admin
        """
        layby = obj.layby
        return format_html(
            f'<strong>Shop Name:</strong> {layby.shop_name}<br>'
            f'<strong>Item Description:</strong> {layby.item_description}<br>'
            f'<strong>Total Cost:</strong> R{layby.total_cost}<br>'
            f'<strong>Expected End Date:</strong> {layby.expected_end_date}<br>'
            f'<strong>Status:</strong> {"Active" if layby.is_active else "Inactive"}<br>'  # noqa: COM812
        )

    layby_details.short_description = "Layby Details"

    def save_model(self, request, obj, form, change):
        if not change:  # This is a new payment being created
            layby = obj.layby
            amount = obj.amount

            # Check if the new payment would exceed the total cost of the layby
            total_paid = Payment.objects.filter(layby=layby).aggregate(
                total=Sum("amount"),
            )["total"] or Decimal("0.00")
            if total_paid + amount > layby.total_cost:
                remaining = layby.total_cost - total_paid
                self.message_user(
                    request,
                    f"Payment of {amount} exceeds the remaining balance of {remaining}. "
                    f"The maximum allowed payment is {remaining}.",
                    level=messages.ERROR,
                )
                return  # Stop the save process

        # Save the payment
        super().save_model(request, obj, form, change)

        if not change:  # Only for new payments
            # Check if the sum of all payments equals the total cost
            new_total_paid = Payment.objects.filter(layby=layby).aggregate(
                total=Sum("amount"),
            )["total"] or Decimal("0.00")
            if new_total_paid == layby.total_cost:
                layby.is_complete = True
                layby.save()

    def response_add(self, request, obj, post_url_continue=None):
        if obj.layby.is_complete:
            self.message_user(
                request,
                "This payment completes the layby!",
                level="SUCCESS",
            )
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if obj.layby.is_complete:
            self.message_user(
                request,
                "This layby is now complete!",
                level="SUCCESS",
            )
        return super().response_change(request, obj)
