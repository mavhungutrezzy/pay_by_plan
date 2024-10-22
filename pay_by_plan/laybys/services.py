from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from laybys.mailer import LaybyMailer
from laybys.models import Layby

User = get_user_model()


class LaybyService:
    @staticmethod
    def create_layby(  # noqa: PLR0913
        user: User,
        shop_name: str,
        item_description: str,
        total_cost: Decimal,
        payment_frequency: str,
        start_date: date | None = None,
        expected_end_date: date | None = None,
        is_active: bool = True,  # noqa: FBT001
        is_complete: bool = False,
    ) -> Layby:
        """
        Create a new layby with the provided details and send confirmation.
        """
        layby = Layby(
            user=user,
            shop_name=shop_name,
            item_description=item_description,
            total_cost=total_cost,
            payment_frequency=payment_frequency,
            start_date=start_date,
            expected_end_date=expected_end_date,
            is_active=is_active,
            is_complete=is_complete,
        )

        layby.full_clean()
        layby.save()

        # Sending confirmation email
        LaybyMailer.send_layby_confirmation(layby=layby)

        return layby

    @staticmethod
    def get_layby(layby_id: int) -> Layby | None:
        """
        Retrieve a layby by its ID.
        """
        return Layby.objects.filter(id=layby_id).first()

    @staticmethod
    def get_user_laybys(user: User) -> QuerySet[Layby]:
        """
        Retrieve all laybys for a specific user.
        """
        return Layby.objects.filter(user=user)

    @staticmethod
    def update_layby(layby: Layby, **kwargs) -> Layby:
        """
        Update a layby with the provided field-value pairs.
        """
        for field, value in kwargs.items():
            if value is not None:
                setattr(layby, field, value)

        layby.full_clean()
        layby.save()

        return layby

    @staticmethod
    def delete_layby(layby: Layby) -> None:
        """
        Delete a layby.
        """
        layby.delete()

    @staticmethod
    def get_active_laybys() -> QuerySet[Layby]:
        """
        Retrieve all active laybys that are not yet complete.
        """
        return Layby.objects.filter(is_active=True, is_complete=False).order_by(
            "-start_date",
        )

    @staticmethod
    def calculate_remaining_balance(layby: Layby) -> Decimal:
        """
        Calculate the remaining balance for a layby.
        """
        return layby.remaining_balance()

    @staticmethod
    def mark_complete(layby: Layby) -> Layby:
        """
        Mark a layby as complete.
        """
        layby.mark_as_complete()
        layby.save()
        return layby

    @staticmethod
    def mark_activate(layby: Layby) -> Layby:
        """Mark a layby as active"""
        layby.mark_as_active()
        layby.save()
        return layby
