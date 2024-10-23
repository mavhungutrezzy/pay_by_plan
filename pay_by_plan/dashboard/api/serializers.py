from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    active_laybys_count = serializers.IntegerField()
    total_remaining_balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_paid_last_30_days = serializers.DecimalField(max_digits=10, decimal_places=2)
    overdue_count = serializers.IntegerField()
    upcoming_reminders_count = serializers.IntegerField()


class DashboardOverviewSerializer(serializers.Serializer):
    summary = DashboardSummarySerializer()
    upcoming_payments = serializers.DictField()
    reminders = serializers.DictField()
    recent_activity = serializers.DictField()
    alerts = serializers.DictField()
