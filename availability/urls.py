from django.urls import path
from .views import (
    HomeView,
    RoomListView,
    RoomDetailView,
    ScheduleListView,
    ScheduleDetailView,
    AddScheduleView,
    DeleteScheduleView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('rooms/', RoomListView.as_view(), name='room_list'),
    path('rooms/<int:pk>/', RoomDetailView.as_view(), name='room_detail'),
    path('schedule/', ScheduleListView.as_view(), name='schedule_list'),
    path('schedule/<int:pk>/', ScheduleDetailView.as_view(), name='schedule_detail'),
    path('schedule/add/', AddScheduleView.as_view(), name='add_schedule'),
    path('schedule/<int:pk>/delete/', DeleteScheduleView.as_view(), name='schedule_delete'),
]