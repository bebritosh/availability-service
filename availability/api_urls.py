from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    RoomViewSet,
    RoomScheduleViewSet,
    WorkingHoursViewSet,
    CheckAvailabilityView,
    AvailableSlotsView,
    HealthCheckView,
    StatsView
)

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'schedule', RoomScheduleViewSet, basename='schedule')
router.register(r'working-hours', WorkingHoursViewSet, basename='working-hours')

urlpatterns = [
    path('', include(router.urls)),
    path('check-availability/', CheckAvailabilityView.as_view(), name='api_check_availability'),
    path('available-slots/', AvailableSlotsView.as_view(), name='api_available_slots'),
    path('health/', HealthCheckView.as_view(), name='api_health'),
    path('stats/', StatsView.as_view(), name='api_stats'),
]