from decimal import Decimal

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from laybys.models import Layby
from payments.models import Payment


class PaymentService:
    @staticmethod
    def create_payment(layby: Layby, amount: Decimal) -> Payment:
        payment = Payment(layby=layby, amount=amount)
        payment.full_clean()
        payment.save()

        if layby.get_total_payments() == layby.total_cost:
            layby.mark_as_complete()
            layby.save()

        return payment

    @staticmethod
    def get_payment(payment_id: int) -> Payment:
        return get_object_or_404(Payment, id=payment_id)

    @staticmethod
    def get_layby_payments(layby: Layby) -> QuerySet[Payment]:
        return Payment.objects.filter(layby=layby)

    @staticmethod
    def update_payment(payment: Payment, amount: Decimal | None = None) -> Payment:
        if amount is not None:
            payment.amount = amount
        payment.save()
        return payment

    @staticmethod
    def delete_payment(payment: Payment) -> None:
        payment.delete()

    @staticmethod
    def get_total_paid(layby: Layby) -> Decimal:
        return sum(payment.amount for payment in layby.payments.all())

    @staticmethod
    def get_recent_payments(days: int = 30) -> QuerySet[Payment]:
        start_date = timezone.now().date() - timezone.timedelta(days=days)
        return Payment.objects.filter(payment_date__gte=start_date)

    @staticmethod
    def get_payments_for_user(user) -> QuerySet[Payment]:
        return Payment.objects.filter(layby__user=user).order_by("-payment_date")

    @staticmethod
    def get_payment_summary(layby: Layby) -> dict:
        total_paid = PaymentService.get_total_paid(layby)
        remaining_balance = layby.total_cost - total_paid
        return {
            "layby_id": layby.id,
            "total_cost": layby.total_cost,
            "total_paid": total_paid,
            "remaining_balance": remaining_balance,
        }

    @staticmethod
    def get_payments(layby_id: int | None = None) -> QuerySet[Payment]:
        if layby_id:
            layby = get_object_or_404(Layby, id=layby_id)
            return PaymentService.get_layby_payments(layby)
        return Payment.objects.all()
