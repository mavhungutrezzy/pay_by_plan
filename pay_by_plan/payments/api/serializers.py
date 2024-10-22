from laybys.api.serializers import LaybySerializer
from laybys.models import Layby
from payments.models import Payment
from rest_framework import serializers


class PaymentSerializer(serializers.ModelSerializer):
    layby = LaybySerializer(read_only=True)
    layby_id = serializers.PrimaryKeyRelatedField(
        source="layby",
        write_only=True,
        queryset=Layby.objects.all(),
    )

    class Meta:
        model = Payment
        fields = [
            "id",
            "layby",
            "layby_id",
            "amount",
            "payment_date",
        ]
        read_only_fields = ["id", "payment_date"]


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["layby", "amount"]
