import django_filters
from laybys.models import Layby


class LaybyFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name="start_date", lookup_expr="gte")
    end_date = django_filters.DateFilter(
        field_name="expected_end_date",
        lookup_expr="lte",
    )
    is_active = django_filters.BooleanFilter(field_name="is_active")
    is_complete = django_filters.BooleanFilter(field_name="is_complete")

    class Meta:
        model = Layby
        fields = ["start_date", "end_date", "is_active", "is_complete"]
