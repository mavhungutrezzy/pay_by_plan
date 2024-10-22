from django.db.models import Sum
from django.utils import timezone
from laybys.models import Layby
from payments.models import Payment


class DashboardService:
    @staticmethod
    def get_user_dashboard(user):
        today = timezone.now().date()
        recent_date = today - timezone.timedelta(days=30)
        upcoming_date = today + timezone.timedelta(days=30)

        active_laybys = Layby.objects.filter(user=user, is_active=True)

        # Calculate total remaining balance
        total_remaining = sum(layby.remaining_balance() for layby in active_laybys)

        upcoming_payments = Payment.objects.filter(
            layby__user=user,
            layby__is_active=True,
            layby__start_date__lte=upcoming_date,
        ).order_by("layby__expected_end_date")

        recent_laybys = Layby.objects.filter(user=user, start_date__gte=recent_date)

        recent_payments = Payment.objects.filter(
            layby__user=user,
            payment_date__gte=recent_date,
        ).order_by("-payment_date")[:10]

        total_paid_recently = (
            recent_payments.aggregate(Sum("amount"))["amount__sum"] or 0
        )

        return {
            "active_laybys_count": active_laybys.count(),
            "total_remaining_balance": total_remaining,
            "total_paid_last_30_days": total_paid_recently,
            "upcoming_payments": [
                {
                    "layby_id": payment.layby.id,
                    "shop_name": payment.layby.shop_name,
                    "amount_due": payment.layby.remaining_balance(),
                    "due_date": payment.layby.expected_end_date,
                }
                for payment in upcoming_payments
            ],
            "recent_laybys": [
                {
                    "id": layby.id,
                    "shop_name": layby.shop_name,
                    "item_description": layby.item_description,
                    "total_cost": layby.total_cost,
                    "remaining_balance": layby.remaining_balance(),
                    "start_date": layby.start_date,
                    "expected_end_date": layby.expected_end_date,
                }
                for layby in recent_laybys
            ],
            "recent_payments": [
                {
                    "id": payment.id,
                    "layby_id": payment.layby.id,
                    "shop_name": payment.layby.shop_name,
                    "amount": payment.amount,
                    "payment_date": payment.payment_date,
                }
                for payment in recent_payments
            ],
        }
