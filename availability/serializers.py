from rest_framework import serializers
from .models import Room, RoomSchedule, WorkingHours


class RoomSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Room
    """

    class Meta:
        model = Room
        fields = ['id', 'number', 'capacity', 'equipment', 'is_active']


class RoomScheduleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели RoomSchedule
    """

    class Meta:
        model = RoomSchedule
        fields = [
            'id',
            'room_number',
            'booking_date',
            'start_time',
            'end_time',
            'booking_type',
            'description',
            'booked_by',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WorkingHoursSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели WorkingHours
    """
    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)

    class Meta:
        model = WorkingHours
        fields = [
            'id',
            'room_number',
            'weekday',
            'weekday_display',
            'start_time',
            'end_time',
            'is_working'
        ]


class AvailabilityCheckSerializer(serializers.Serializer):
    """
    Сериализатор для проверки доступности
    """
    room_number = serializers.CharField(max_length=50)
    booking_date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    booking_type = serializers.ChoiceField(
        choices=['lesson', 'exam', 'meeting'],
        default='lesson'
    )

    def validate(self, data):
        """Проверка времени"""
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError(
                "Время начала должно быть раньше времени окончания"
            )
        return data