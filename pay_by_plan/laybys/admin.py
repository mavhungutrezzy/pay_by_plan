from django.contrib import admin
from django.utils.html import format_html
from payments.models import Payment
from django.contrib import admin
from allauth.account.decorators import secure_admin_login

admin.autodiscover()
from .models import Layby


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    readonly_fields = ("amount", "payment_date")
    can_delete = False


@admin.register(Layby)
class LaybyAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "shop_name",
        "item_description_truncated",
        "total_cost",
        "remaining_balance",
        "is_active",
        "is_complete",
        "expected_end_date",
    )
    list_filter = ("is_active", "is_complete", "shop_name", "expected_end_date")
    search_fields = ("shop_name", "user__username", "user__email")
    readonly_fields = ("remaining_balance_display",)
    inlines = [PaymentInline]

    def remaining_balance_display(self, obj):
        remaining = obj.remaining_balance()
        return format_html(f"<b>R{remaining:.2f}</b>")

    remaining_balance_display.short_description = "Remaining Balance"

    def item_description_truncated(self, obj):
        max_description_length = 30
        description = obj.item_description

        if len(description) > max_description_length:
            return f"{description[:max_description_length]}..."

        return description

    item_description_truncated.short_description = "Item Description"
