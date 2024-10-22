from rest_framework.routers import DefaultRouter

from .views import LaybyViewSet

router = DefaultRouter()
router.register("laybys", LaybyViewSet, basename="layby")

urlpatterns = router.urls
