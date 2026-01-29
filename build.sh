#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Создать суперпользователя
python manage.py shell <<'EOFMARKER'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'Admin123456')
    print('✅ Суперпользователь создан')
else:
    print('ℹ️ Суперпользователь уже существует')
EOFMARKER

# Создать тестовые данные
python manage.py shell <<'EOFMARKER'
from availability.models import Room, RoomSchedule
from datetime import date, time, timedelta

if Room.objects.count() == 0:
    print('📍 Создание тестовых аудиторий...')
    Room.objects.create(number='101', capacity=30, equipment='Проектор, доска', is_active=True)
    Room.objects.create(number='102', capacity=50, equipment='Компьютеры', is_active=True)
    Room.objects.create(number='103', capacity=25, equipment='Доска', is_active=True)
    Room.objects.create(number='104', capacity=40, equipment='Лаборатория', is_active=True)
    Room.objects.create(number='201', capacity=35, equipment='Проектор, микрофон', is_active=True)
    print(f'✅ Создано аудиторий: {Room.objects.count()}')
else:
    print(f'ℹ️ Аудитории уже существуют ({Room.objects.count()} шт)')

if RoomSchedule.objects.count() == 0:
    print('📅 Создание тестовых бронирований...')
    tomorrow = date.today() + timedelta(days=1)
    next_week = date.today() + timedelta(days=7)
    
    RoomSchedule.objects.create(
        room_number='101',
        booking_date=tomorrow,
        start_time=time(10, 0),
        end_time=time(12, 0),
        booking_type='lesson',
        booked_by='teacher1@example.com',
        description='Лекция по математике'
    )
    
    RoomSchedule.objects.create(
        room_number='101',
        booking_date=tomorrow,
        start_time=time(14, 0),
        end_time=time(16, 0),
        booking_type='lesson',
        booked_by='teacher2@example.com',
        description='Практическое занятие'
    )
    
    RoomSchedule.objects.create(
        room_number='102',
        booking_date=tomorrow,
        start_time=time(9, 0),
        end_time=time(11, 0),
        booking_type='exam',
        booked_by='teacher3@example.com',
        description='Экзамен по программированию'
    )
    
    RoomSchedule.objects.create(
        room_number='103',
        booking_date=next_week,
        start_time=time(15, 0),
        end_time=time(17, 0),
        booking_type='meeting',
        booked_by='admin@example.com',
        description='Собрание кафедры'
    )
    
    RoomSchedule.objects.create(
        room_number='201',
        booking_date=tomorrow,
        start_time=time(12, 0),
        end_time=time(14, 0),
        booking_type='lesson',
        booked_by='teacher4@example.com',
        description='Семинар'
    )
    
    print(f'✅ Создано бронирований: {RoomSchedule.objects.count()}')
else:
    print(f'ℹ️ Бронирования уже существуют ({RoomSchedule.objects.count()} шт)')

print('🎉 Инициализация базы данных завершена!')
EOFMARKER