from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Room, RoomSchedule, WorkingHours


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['number', 'capacity', 'is_active']
    list_filter = ['is_active']
    search_fields = ['number', 'equipment']
    ordering = ['number']


@admin.register(RoomSchedule)
class RoomScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'room_number',
        'booking_date',
        'start_time',
        'end_time',
        'booking_type',
        'booked_by',
        'created_at'
    ]
    list_filter = ['booking_type', 'booking_date', 'room_number']
    search_fields = ['room_number', 'booked_by', 'description']
    date_hierarchy = 'booking_date'
    ordering = ['-booking_date', 'start_time']


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = [
        'room_number',
        'weekday',
        'start_time',
        'end_time',
        'is_working'
    ]
    list_filter = ['weekday', 'is_working', 'room_number']
    ordering = ['room_number', 'weekday']