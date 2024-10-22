# serializers.py
from laybys.models import Layby
from rest_framework import serializers


class LaybySerializer(serializers.ModelSerializer):
    """Basic layby serializer for list views."""

    class Meta:
        model = Layby
        exclude = ("user",)


class LaybyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating laybys."""

    class Meta:
        model = Layby
        exclude = ("user", "is_active", "is_complete")


class LaybyUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating laybys."""

    class Meta:
        model = Layby
        exclude = ("user", "total_cost")


class LaybyDetailSerializer(serializers.ModelSerializer):
    """Detailed layby serializer with additional fields."""

    remaining_balance = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    progress_percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = Layby
        exclude = ("user",)
