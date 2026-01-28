from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Room, RoomSchedule, WorkingHours
from .serializers import (
    RoomSerializer,
    RoomScheduleSerializer,
    WorkingHoursSerializer,
    AvailabilityCheckSerializer
)
from .services import AvailabilityChecker


class RoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления аудиториями

    Endpoints:
    - GET /api/rooms/ - список всех аудиторий
    - GET /api/rooms/{id}/ - детали аудитории
    - POST /api/rooms/ - создание аудитории
    - PUT /api/rooms/{id}/ - обновление аудитории
    - DELETE /api/rooms/{id}/ - удаление аудитории
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_queryset(self):
        """Фильтрация активных аудиторий"""
        queryset = Room.objects.all()
        is_active = self.request.query_params.get('is_active', None)

        if is_active is not None:
            is_active_bool = is_active.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_active=is_active_bool)

        return queryset


class RoomScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления расписанием аудиторий

    Endpoints:
    - GET /api/schedule/ - список всех бронирований
    - GET /api/schedule/{id}/ - детали бронирования
    - POST /api/schedule/ - создание бронирования
    - DELETE /api/schedule/{id}/ - удаление бронирования
    """
    queryset = RoomSchedule.objects.all()
    serializer_class = RoomScheduleSerializer

    def get_queryset(self):
        """Фильтрация по аудитории и дате"""
        queryset = RoomSchedule.objects.all()

        room_number = self.request.query_params.get('room_number', None)
        booking_date = self.request.query_params.get('booking_date', None)

        if room_number:
            queryset = queryset.filter(room_number=room_number)

        if booking_date:
            queryset = queryset.filter(booking_date=booking_date)

        return queryset


class WorkingHoursViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления рабочими часами
    """
    queryset = WorkingHours.objects.all()
    serializer_class = WorkingHoursSerializer

    def get_queryset(self):
        """Фильтрация по аудитории"""
        queryset = WorkingHours.objects.all()
        room_number = self.request.query_params.get('room_number', None)

        if room_number:
            queryset = queryset.filter(room_number=room_number)

        return queryset


class CheckAvailabilityView(APIView):
    """
    API для проверки доступности аудитории

    POST /api/check-availability/

    Request body:
    {
        "room_number": "101",
        "booking_date": "2026-02-15",
        "start_time": "10:00",
        "end_time": "12:00",
        "booking_type": "lesson"
    }

    Response (доступна):
    {
        "available": true,
        "message": "Аудитория 101 доступна для бронирования",
        "conflicts": [],
        "reason": null
    }

    Response (недоступна):
    {
        "available": false,
        "message": "Аудитория занята в указанное время",
        "conflicts": ["Конфликт с 10:00-11:30 (Занятие)"],
        "reason": "time_conflict"
    }
    """

    def post(self, request):
        serializer = AvailabilityCheckSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'available': False,
                'message': 'Ошибка валидации данных',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        check_data = serializer.validated_data

        try:
            checker = AvailabilityChecker()
            result = checker.check_availability(check_data)

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'available': False,
                'message': f'Ошибка при проверке доступности: {str(e)}',
                'conflicts': [],
                'reason': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AvailableSlotsView(APIView):
    """
    API для получения списка доступных временных слотов

    GET /api/available-slots/?room_number=101&booking_date=2026-02-15

    Response:
    {
        "room_number": "101",
        "booking_date": "2026-02-15",
        "available_slots": [
            {"start": "08:00", "end": "10:00"},
            {"start": "12:00", "end": "14:00"},
            {"start": "16:00", "end": "20:00"}
        ]
    }
    """

    def get(self, request):
        room_number = request.query_params.get('room_number')
        booking_date = request.query_params.get('booking_date')

        if not room_number or not booking_date:
            return Response({
                'error': 'Требуются параметры: room_number и booking_date'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            from datetime import datetime
            date_obj = datetime.strptime(booking_date, '%Y-%m-%d').date()

            checker = AvailabilityChecker()
            available_slots = checker.get_available_slots(room_number, date_obj)

            return Response({
                'room_number': room_number,
                'booking_date': booking_date,
                'available_slots': available_slots
            })

        except ValueError:
            return Response({
                'error': 'Неверный формат даты. Используйте YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Ошибка: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheckView(APIView):
    """
    Проверка работоспособности сервиса
    GET /api/health/
    """

    def get(self, request):
        return Response({
            'status': 'ok',
            'service': 'availability-service',
            'version': '1.0.0'
        })


class StatsView(APIView):
    """
    Статистика по бронированиям
    GET /api/stats/
    """

    def get(self, request):
        total_rooms = Room.objects.count()
        active_rooms = Room.objects.filter(is_active=True).count()
        total_bookings = RoomSchedule.objects.count()

        # Статистика по типам бронирований
        lessons = RoomSchedule.objects.filter(booking_type='lesson').count()
        exams = RoomSchedule.objects.filter(booking_type='exam').count()
        meetings = RoomSchedule.objects.filter(booking_type='meeting').count()

        return Response({
            'total_rooms': total_rooms,
            'active_rooms': active_rooms,
            'total_bookings': total_bookings,
            'by_type': {
                'lessons': lessons,
                'exams': exams,
                'meetings': meetings
            }
        })