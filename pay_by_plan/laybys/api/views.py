from django.db.models import QuerySet
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from laybys.filters import LaybyFilter
from laybys.models import Layby
from laybys.services import LaybyService
from rest_framework import filters
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import LaybyCreateSerializer
from .serializers import LaybyDetailSerializer
from .serializers import LaybySerializer
from .serializers import LaybyUpdateSerializer


@extend_schema(tags=["laybys"])
class LaybyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing laybys.
    Provides CRUD operations and additional actions for layby management.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = LaybyFilter

    def get_queryset(self) -> QuerySet[Layby]:
        """Get laybys for the current user with optional filters."""
        return LaybyService.get_user_laybys(self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return LaybyCreateSerializer
        if self.action in ["update", "partial_update"]:
            return LaybyUpdateSerializer
        if self.action in ["retrieve", "complete", "deactivate"]:
            return LaybyDetailSerializer
        return LaybySerializer

    def perform_create(self, serializer):
        """Create a new layby."""
        return LaybyService.create_layby(
            user=self.request.user,
            **serializer.validated_data,
        )

    def perform_update(self, serializer):
        """Update an existing layby."""
        return LaybyService.update_layby(
            self.get_object(),
            **serializer.validated_data,
        )

    def perform_destroy(self, instance):
        """Delete a layby."""
        LaybyService.delete_layby(instance)

    @action(detail=False, methods=["get"])
    def overdue(self, request: Request) -> Response:
        """List overdue laybys."""
        laybys = self.get_queryset().filter(
            is_active=True,
            is_complete=False,
            expected_end_date__lt=timezone.now().date(),
        )
        serializer = LaybySerializer(laybys, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def complete(self, request: Request, pk=None) -> Response:
        """Mark the layby as complete."""
        layby = self.get_object()
        try:
            completed_layby = LaybyService.mark_complete(layby)
            return Response(LaybyDetailSerializer(completed_layby).data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"])
    def deactivate(self, request: Request, pk=None) -> Response:
        """Mark a layby as inactive."""
        layby = self.get_object()
        try:
            active_layby = LaybyService.mark_activate(layby)
            return Response(LaybyDetailSerializer(active_layby).data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
