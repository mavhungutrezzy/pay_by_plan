from drf_spectacular.utils import extend_schema
from laybys.models import Layby
from payments.services import PaymentService
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pay_by_plan.payments.api.serializers import PaymentSerializer


@extend_schema(tags=["payments"])
class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payments.
    Provides CRUD operations and additional actions for payment management.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        """Get payments for the current user."""
        return PaymentService.get_payments_for_user(self.request.user)

    def retrieve(self, request, pk=None):
        """Retrieve a specific payment."""
        payment = PaymentService.get_payment(pk)
        serializer = self.get_serializer(payment)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Create a new payment for a layby."""
        layby_id = request.data.get(
            "layby_id",
        )  # Assuming layby_id is passed in request data
        layby = Layby.objects.get(id=layby_id)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            payment = PaymentService.create_payment(
                layby,
                serializer.validated_data["amount"],
            )
            return Response(
                self.get_serializer(payment).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        """Update an existing payment."""
        payment = PaymentService.get_payment(pk)
        serializer = self.get_serializer(payment, data=request.data, partial=True)

        if serializer.is_valid():
            payment = PaymentService.update_payment(
                payment,
                serializer.validated_data.get("amount"),
            )
            return Response(self.get_serializer(payment).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """Delete a payment."""
        payment = PaymentService.get_payment(pk)
        PaymentService.delete_payment(payment)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def layby_payments(self, request):
        """Get payments for a specific layby."""
        layby_id = request.query_params.get("layby_id")
        layby = Layby.objects.get(id=layby_id)
        payments = PaymentService.get_layby_payments(layby)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get payment summary for a layby."""
        layby_id = request.query_params.get("layby_id")
        layby = Layby.objects.get(id=layby_id)
        summary = PaymentService.get_payment_summary(layby)
        return Response(summary)

    @action(detail=False, methods=["get"])
    def recent(self, request):
        """Get recent payments."""
        days = int(request.query_params.get("days", 30))
        payments = PaymentService.get_recent_payments(days)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)
