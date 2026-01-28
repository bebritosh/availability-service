from django.db import models

# Create your models here.
from django.db import models
from django.core.exceptions import ValidationError
from datetime import time


class Room(models.Model):
    """
    Модель аудитории
    """
    number = models.CharField(max_length=50, unique=True, verbose_name='Номер аудитории')
    capacity = models.IntegerField(default=30, verbose_name='Вместимость')
    equipment = models.TextField(blank=True, verbose_name='Оборудование')
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta:
        verbose_name = 'Аудитория'
        verbose_name_plural = 'Аудитории'
        ordering = ['number']

    def __str__(self):
        return f"Аудитория {self.number}"


class RoomSchedule(models.Model):
    """
    Модель расписания аудитории (занятые временные слоты)
    """
    BOOKING_TYPE_CHOICES = [
        ('lesson', 'Занятие'),
        ('exam', 'Экзамен'),
        ('meeting', 'Собрание'),
    ]

    room_number = models.CharField(max_length=50, verbose_name='Номер аудитории')
    booking_date = models.DateField(verbose_name='Дата бронирования')
    start_time = models.TimeField(verbose_name='Время начала')
    end_time = models.TimeField(verbose_name='Время окончания')
    booking_type = models.CharField(
        max_length=20,
        choices=BOOKING_TYPE_CHOICES,
        default='lesson',
        verbose_name='Тип бронирования'
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    booked_by = models.EmailField(verbose_name='Забронировал')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Расписание аудитории'
        verbose_name_plural = 'Расписание аудиторий'
        ordering = ['booking_date', 'start_time']
        indexes = [
            models.Index(fields=['room_number', 'booking_date']),
        ]

    def __str__(self):
        return f"{self.room_number} - {self.booking_date} ({self.start_time}-{self.end_time})"

    def clean(self):
        """Валидация данных"""
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError('Время начала должно быть раньше времени окончания')


class WorkingHours(models.Model):
    """
    Модель рабочих часов аудиторий
    """
    WEEKDAY_CHOICES = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    ]

    room_number = models.CharField(max_length=50, verbose_name='Номер аудитории')
    weekday = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        verbose_name='День недели'
    )
    start_time = models.TimeField(default=time(8, 0), verbose_name='Начало работы')
    end_time = models.TimeField(default=time(20, 0), verbose_name='Конец работы')
    is_working = models.BooleanField(default=True, verbose_name='Рабочий день')

    class Meta:
        verbose_name = 'Рабочие часы'
        verbose_name_plural = 'Рабочие часы'
        unique_together = ['room_number', 'weekday']

    def __str__(self):
        day_name = dict(self.WEEKDAY_CHOICES)[self.weekday]
        return f"{self.room_number} - {day_name}: {self.start_time}-{self.end_time}"