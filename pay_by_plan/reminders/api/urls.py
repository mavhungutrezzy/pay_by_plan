from rest_framework.routers import DefaultRouter

from .views import NotificationViewSet
from .views import ReminderViewSet

router = DefaultRouter()
router.register("reminders", ReminderViewSet, basename="reminder")
router.register("notifications", NotificationViewSet, basename="notification")

urlpatterns = router.urls
