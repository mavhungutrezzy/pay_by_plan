from django.db.models import Sum
from django.utils import timezone
from laybys.models import Layby
from payments.models import Payment
from reminders.models import Reminder


class DashboardService:
    @staticmethod
    def get_user_dashboard_overview(user):
        today = timezone.now().date()
        recent_date = today - timezone.timedelta(days=30)
        upcoming_date = today + timezone.timedelta(days=30)

        # Core Data
        active_laybys = Layby.objects.filter(user=user, is_active=True)
        total_remaining = sum(layby.remaining_balance() for layby in active_laybys)

        # Payments Data
        recent_payments = Payment.objects.filter(
            layby__user=user,
            payment_date__gte=recent_date,
        ).order_by("-payment_date")[:10]

        total_paid_recently = (
            recent_payments.aggregate(Sum("amount"))["amount__sum"] or 0
        )

        # Reminders Data
        upcoming_reminders = Reminder.objects.filter(
            layby__user=user,
            is_active=True,
            next_reminder_date__lte=upcoming_date,
        ).order_by("next_reminder_date")

        # Overdue Items
        overdue_laybys = active_laybys.filter(expected_end_date__lt=today)

        return {
            "summary": {
                "active_laybys_count": active_laybys.count(),
                "total_remaining_balance": total_remaining,
                "total_paid_last_30_days": total_paid_recently,
                "overdue_count": overdue_laybys.count(),
                "upcoming_reminders_count": upcoming_reminders.count(),
            },
            "upcoming_payments": {
                "due_this_week": DashboardService._get_upcoming_payments(user, days=7),
                "due_this_month": DashboardService._get_upcoming_payments(
                    user,
                    days=30,
                ),
            },
            "reminders": {
                "upcoming": [
                    {
                        "id": reminder.id,
                        "layby_id": reminder.layby.id,
                        "shop_name": reminder.layby.shop_name,
                        "next_reminder_date": reminder.next_reminder_date,
                        "frequency": reminder.frequency,
                        "remaining_balance": reminder.layby.remaining_balance(),
                    }
                    for reminder in upcoming_reminders[:5]
                ],
            },
            "recent_activity": {
                "laybys": DashboardService._get_recent_laybys(user),
                "payments": DashboardService._get_recent_payments(user),
            },
            "alerts": DashboardService._get_user_alerts(user),
        }

    @staticmethod
    def get_user_statistics(user):
        return {
            "payment_trends": DashboardService._get_payment_trends(user),
            "layby_status_distribution": DashboardService._get_layby_distribution(user),
            "monthly_payment_summary": DashboardService._get_monthly_summary(user),
            "completion_rate": DashboardService._get_completion_rate(user),
        }

    @staticmethod
    def _get_upcoming_payments(user, days):
        end_date = timezone.now().date() + timezone.timedelta(days=days)
        return [
            {
                "layby_id": layby.id,
                "shop_name": layby.shop_name,
                "amount_due": layby.remaining_balance(),
                "due_date": layby.expected_end_date,
                "progress_percentage": layby.payment_progress(),
                "has_reminder": hasattr(layby, "reminder"),
            }
            for layby in Layby.objects.filter(
                user=user,
                is_active=True,
                expected_end_date__lte=end_date,
            )
        ]

    @staticmethod
    def _get_user_alerts(user):
        today = timezone.now().date()
        return {
            "overdue_payments": [
                {
                    "layby_id": layby.id,
                    "shop_name": layby.shop_name,
                    "days_overdue": (today - layby.expected_end_date).days,
                    "remaining_balance": layby.remaining_balance(),
                }
                for layby in Layby.objects.filter(
                    user=user,
                    is_active=True,
                    expected_end_date__lt=today,
                )
            ],
            "inactive_reminders": [
                {"layby_id": reminder.layby.id, "shop_name": reminder.layby.shop_name}
                for reminder in Reminder.objects.filter(
                    layby__user=user,
                    is_active=False,
                    layby__is_active=True,
                )
            ],
        }
