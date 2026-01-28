from datetime import datetime, time
from typing import Dict, List, Any
from django.conf import settings
from .models import RoomSchedule, WorkingHours
import logging

logger = logging.getLogger(__name__)


class AvailabilityChecker:
    """
    Сервис для проверки доступности аудиторий
    """

    def __init__(self):
        self.business_hours_start = time.fromisoformat(
            settings.BUSINESS_HOURS.get('start', '08:00')
        )
        self.business_hours_end = time.fromisoformat(
            settings.BUSINESS_HOURS.get('end', '20:00')
        )

    def check_availability(self, check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Основной метод проверки доступности аудитории

        Args:
            check_data: Данные для проверки (room_number, booking_date, start_time, end_time, booking_type)

        Returns:
            Результат проверки с полями: available, message, conflicts
        """
        room_number = check_data['room_number']
        booking_date = check_data['booking_date']
        start_time = check_data['start_time']
        end_time = check_data['end_time']
        booking_type = check_data.get('booking_type', 'lesson')

        logger.info(f"Проверка доступности: {room_number} на {booking_date} {start_time}-{end_time}")

        # Сценарий 1: Проверка конфликтов по времени
        conflicts = self._check_time_conflicts(room_number, booking_date, start_time, end_time)
        if conflicts:
            return {
                'available': False,
                'message': f'Аудитория занята в указанное время. Найдено конфликтов: {len(conflicts)}',
                'conflicts': conflicts,
                'reason': 'time_conflict'
            }

        # Сценарий 2: Проверка рабочего времени
        working_hours_check = self._check_working_hours(room_number, booking_date, start_time, end_time)
        if not working_hours_check['is_working']:
            return {
                'available': False,
                'message': working_hours_check['message'],
                'conflicts': [],
                'reason': 'outside_working_hours'
            }

        # Сценарий 3: Проверка типа бронирования (специальные правила)
        type_check = self._check_booking_type_rules(room_number, booking_date, start_time, end_time, booking_type)
        if not type_check['allowed']:
            return {
                'available': False,
                'message': type_check['message'],
                'conflicts': [],
                'reason': 'booking_type_restriction'
            }

        # Всё ок - аудитория доступна
        return {
            'available': True,
            'message': f'Аудитория {room_number} доступна для бронирования',
            'conflicts': [],
            'reason': None
        }

    def _check_time_conflicts(
            self,
            room_number: str,
            booking_date,
            start_time: time,
            end_time: time
    ) -> List[str]:
        """
        Проверка конфликтов по времени (Сценарий 1)
        """
        # Находим все существующие бронирования на эту дату и аудиторию
        existing_bookings = RoomSchedule.objects.filter(
            room_number=room_number,
            booking_date=booking_date
        )

        conflicts = []

        for booking in existing_bookings:
            # Проверяем пересечение временных интервалов
            if self._times_overlap(start_time, end_time, booking.start_time, booking.end_time):
                conflict_msg = (
                    f"Конфликт с существующим бронированием: "
                    f"{booking.start_time.strftime('%H:%M')}-{booking.end_time.strftime('%H:%M')} "
                    f"({booking.get_booking_type_display()})"
                )
                conflicts.append(conflict_msg)

        return conflicts

    def _times_overlap(self, start1: time, end1: time, start2: time, end2: time) -> bool:
        """
        Проверка пересечения двух временных интервалов
        """
        return start1 < end2 and end1 > start2

    def _check_working_hours(
            self,
            room_number: str,
            booking_date,
            start_time: time,
            end_time: time
    ) -> Dict[str, Any]:
        """
        Проверка рабочего времени (Сценарий 2)
        """
        weekday = booking_date.weekday()

        # Пытаемся найти специфичные рабочие часы для этой аудитории
        try:
            working_hours = WorkingHours.objects.get(
                room_number=room_number,
                weekday=weekday
            )

            if not working_hours.is_working:
                return {
                    'is_working': False,
                    'message': f'Аудитория не работает в {working_hours.get_weekday_display()}'
                }

            room_start = working_hours.start_time
            room_end = working_hours.end_time

        except WorkingHours.DoesNotExist:
            # Используем стандартные рабочие часы
            room_start = self.business_hours_start
            room_end = self.business_hours_end

        # Проверяем, что бронирование в пределах рабочих часов
        if start_time < room_start or end_time > room_end:
            return {
                'is_working': False,
                'message': (
                    f'Бронирование выходит за рамки рабочих часов аудитории. '
                    f'Рабочее время: {room_start.strftime("%H:%M")}-{room_end.strftime("%H:%M")}'
                )
            }

        return {
            'is_working': True,
            'message': 'Бронирование в пределах рабочих часов'
        }

    def _check_booking_type_rules(
            self,
            room_number: str,
            booking_date,
            start_time: time,
            end_time: time,
            booking_type: str
    ) -> Dict[str, Any]:
        """
        Проверка правил для типа бронирования (Сценарий 3)
        """
        # Правило 1: Экзамены требуют минимум 2 часа
        if booking_type == 'exam':
            duration_hours = (
                                     datetime.combine(booking_date, end_time) -
                                     datetime.combine(booking_date, start_time)
                             ).total_seconds() / 3600

            if duration_hours < 2:
                return {
                    'allowed': False,
                    'message': 'Для экзамена требуется минимум 2 часа бронирования'
                }

        # Правило 2: Собрания не могут быть длиннее 4 часов
        if booking_type == 'meeting':
            duration_hours = (
                                     datetime.combine(booking_date, end_time) -
                                     datetime.combine(booking_date, start_time)
                             ).total_seconds() / 3600

            if duration_hours > 4:
                return {
                    'allowed': False,
                    'message': 'Собрание не может длиться более 4 часов'
                }

        # Правило 3: Занятия не раньше 8:00 и не позже 18:00 (начало)
        if booking_type == 'lesson':
            if start_time < time(8, 0) or start_time >= time(18, 0):
                return {
                    'allowed': False,
                    'message': 'Занятия могут начинаться только с 08:00 до 18:00'
                }

        return {
            'allowed': True,
            'message': 'Тип бронирования соответствует правилам'
        }

    def get_available_slots(
            self,
            room_number: str,
            booking_date,
            duration_minutes: int = 120
    ) -> List[Dict[str, str]]:
        """
        Получить список доступных временных слотов для аудитории
        """
        # Получаем все занятые слоты
        busy_slots = RoomSchedule.objects.filter(
            room_number=room_number,
            booking_date=booking_date
        ).order_by('start_time')

        # Определяем рабочие часы
        weekday = booking_date.weekday()
        try:
            working_hours = WorkingHours.objects.get(
                room_number=room_number,
                weekday=weekday
            )
            if not working_hours.is_working:
                return []
            work_start = working_hours.start_time
            work_end = working_hours.end_time
        except WorkingHours.DoesNotExist:
            work_start = self.business_hours_start
            work_end = self.business_hours_end

        # Находим свободные слоты
        available_slots = []
        current_time = work_start

        for slot in busy_slots:
            if current_time < slot.start_time:
                # Есть свободное время перед этим слотом
                available_slots.append({
                    'start': current_time.strftime('%H:%M'),
                    'end': slot.start_time.strftime('%H:%M')
                })
            current_time = max(current_time, slot.end_time)

        # Проверяем время после последнего слота
        if current_time < work_end:
            available_slots.append({
                'start': current_time.strftime('%H:%M'),
                'end': work_end.strftime('%H:%M')
            })

        return available_slots