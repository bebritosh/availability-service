# 🔍 Availability Service (Студент B) - Сервис проверки доступности

Веб-сервис для проверки доступности аудиторий с реализацией всех сценариев проверки.

## 📋 Описание

Django-приложение для проверки доступности аудиторий (Студент B), которое:
- Проверяет конфликты по времени
- Проверяет рабочие часы аудиторий
- Проверяет соответствие типам бронирования
- Предоставляет REST API для интеграции
- Имеет веб-интерфейс для управления

## 🚀 Функциональность

### Реализованные сценарии:

#### Сценарий 1: Проверка конфликтов
Проверяет, занята ли аудитория в указанное время.

**Пример ответа при конфликте:**
```json
{
  "available": false,
  "message": "Аудитория занята в указанное время",
  "conflicts": ["Конфликт с 10:00-11:30 (Занятие)"],
  "reason": "time_conflict"
}
```

#### Сценарий 2: Проверка рабочего времени
Проверяет доступность аудитории в рабочие часы (по умолчанию 08:00–20:00).

**Пример ответа:**
```json
{
  "available": false,
  "message": "Бронирование выходит за рамки рабочих часов. Рабочее время: 08:00-20:00",
  "conflicts": [],
  "reason": "outside_working_hours"
}
```

#### Сценарий 3: Проверка типа бронирования
Проверяет соответствие правилам для типов бронирования:
- **Экзамены**: минимум 2 часа
- **Собрания**: максимум 4 часа
- **Занятия**: начало с 08:00 до 18:00

**Пример ответа:**
```json
{
  "available": false,
  "message": "Для экзамена требуется минимум 2 часа бронирования",
  "conflicts": [],
  "reason": "booking_type_restriction"
}
```

## 🛠 Технологический стек

- **Backend**: Django 4.2.7, Django REST Framework 3.14.0
- **Database**: SQLite (development), PostgreSQL (production)
- **Deployment**: Gunicorn, Whitenoise

## 📦 Установка и запуск

### Локальная разработка:

1. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

2. **Создайте файл .env:**
```bash
cp .env.example .env
```

3. **Выполните миграции:**
```bash
python manage.py migrate
```

4. **Создайте тестовые данные (опционально):**
```bash
python manage.py shell
```
```python
from availability.models import Room, RoomSchedule, WorkingHours
from datetime import date, time

# Создать аудитории
Room.objects.create(number="101", capacity=30, equipment="Проектор, доска")
Room.objects.create(number="102", capacity=50, equipment="Компьютеры")

# Создать тестовое бронирование
RoomSchedule.objects.create(
    room_number="101",
    booking_date=date(2026, 2, 15),
    start_time=time(10, 0),
    end_time=time(12, 0),
    booking_type="lesson",
    booked_by="test@example.com"
)
```

5. **Запустите сервер:**
```bash
python manage.py runserver 8001
```

Сервис будет доступен по адресу: http://localhost:8001

## 🌐 Развёртывание на Render

См. файл `DEPLOYMENT_GUIDE.md` для подробных инструкций.

**Краткая версия:**
1. Загрузите проект на GitHub
2. Создайте Web Service на Render
3. Build Command: `./build.sh`
4. Start Command: `gunicorn availability_project.wsgi:application`
5. Добавьте переменные окружения

## 🔌 API Endpoints

### REST API:

#### 1. Проверка доступности (ОСНОВНОЙ ENDPOINT)
```http
POST /api/check-availability/
Content-Type: application/json

{
  "room_number": "101",
  "booking_date": "2026-02-15",
  "start_time": "10:00",
  "end_time": "12:00",
  "booking_type": "lesson"
}
```

**Response (доступна):**
```json
{
  "available": true,
  "message": "Аудитория 101 доступна для бронирования",
  "conflicts": [],
  "reason": null
}
```

**Response (недоступна):**
```json
{
  "available": false,
  "message": "Аудитория занята в указанное время",
  "conflicts": ["Конфликт с 10:00-12:00 (Занятие)"],
  "reason": "time_conflict"
}
```

#### 2. Доступные временные слоты
```http
GET /api/available-slots/?room_number=101&booking_date=2026-02-15
```

**Response:**
```json
{
  "room_number": "101",
  "booking_date": "2026-02-15",
  "available_slots": [
    {"start": "08:00", "end": "10:00"},
    {"start": "12:00", "end": "14:00"}
  ]
}
```

#### 3. Управление аудиториями
```http
GET /api/rooms/                # Список аудиторий
GET /api/rooms/{id}/           # Детали аудитории
POST /api/rooms/               # Создать аудиторию
PUT /api/rooms/{id}/           # Обновить аудиторию
DELETE /api/rooms/{id}/        # Удалить аудиторию
```

#### 4. Управление расписанием
```http
GET /api/schedule/             # Список всех бронирований
GET /api/schedule/{id}/        # Детали бронирования
POST /api/schedule/            # Создать бронирование
DELETE /api/schedule/{id}/     # Удалить бронирование
```

#### 5. Рабочие часы
```http
GET /api/working-hours/                    # Список рабочих часов
GET /api/working-hours/?room_number=101   # Для конкретной аудитории
POST /api/working-hours/                   # Добавить рабочие часы
```

#### 6. Статистика
```http
GET /api/stats/
```

**Response:**
```json
{
  "total_rooms": 10,
  "active_rooms": 8,
  "total_bookings": 45,
  "by_type": {
    "lessons": 30,
    "exams": 10,
    "meetings": 5
  }
}
```

#### 7. Health Check
```http
GET /api/health/
```

### Web Interface:
- `GET /` - Форма проверки доступности
- `GET /rooms/` - Список аудиторий
- `GET /rooms/{id}/` - Детали аудитории
- `GET /schedule/` - Расписание
- `GET /schedule/add/` - Добавить бронирование

## 📊 Структура базы данных

### Модель Room (Аудитория):
| Поле | Тип | Описание |
|------|-----|----------|
| number | String | Номер аудитории (уникальный) |
| capacity | Integer | Вместимость |
| equipment | Text | Оборудование |
| is_active | Boolean | Активна |

### Модель RoomSchedule (Расписание):
| Поле | Тип | Описание |
|------|-----|----------|
| room_number | String | Номер аудитории |
| booking_date | Date | Дата бронирования |
| start_time | Time | Время начала |
| end_time | Time | Время окончания |
| booking_type | String | Тип (lesson/exam/meeting) |
| description | Text | Описание |
| booked_by | Email | Email бронировавшего |
| created_at | DateTime | Дата создания |

### Модель WorkingHours (Рабочие часы):
| Поле | Тип | Описание |
|------|-----|----------|
| room_number | String | Номер аудитории |
| weekday | Integer | День недели (0-6) |
| start_time | Time | Начало работы |
| end_time | Time | Конец работы |
| is_working | Boolean | Рабочий день |

## 🧪 Тестовые сценарии

### Сценарий 1: Успешная проверка
```bash
curl -X POST http://localhost:8001/api/check-availability/ \
  -H "Content-Type: application/json" \
  -d '{
    "room_number": "101",
    "booking_date": "2026-03-01",
    "start_time": "14:00",
    "end_time": "16:00",
    "booking_type": "lesson"
  }'
```

### Сценарий 2: Конфликт по времени
1. Создайте бронирование на 10:00-12:00
2. Попробуйте создать бронирование на 11:00-13:00
3. Получите ответ с конфликтом

### Сценарий 3: Нарушение рабочих часов
```bash
curl -X POST http://localhost:8001/api/check-availability/ \
  -H "Content-Type: application/json" \
  -d '{
    "room_number": "101",
    "booking_date": "2026-03-01",
    "start_time": "21:00",
    "end_time": "22:00",
    "booking_type": "lesson"
  }'
```

### Сценарий 4: Нарушение правил типа
```bash
# Экзамен менее 2 часов
curl -X POST http://localhost:8001/api/check-availability/ \
  -H "Content-Type: application/json" \
  -d '{
    "room_number": "101",
    "booking_date": "2026-03-01",
    "start_time": "10:00",
    "end_time": "11:00",
    "booking_type": "exam"
  }'
```

## 🎨 Веб-интерфейс

### Главная страница:
- Форма проверки доступности
- Правила бронирования
- Последние проверки

### Аудитории:
- Список всех аудиторий
- Фильтрация активных/неактивных
- Детальная информация с расписанием

### Расписание:
- Список всех бронирований
- Фильтры по аудитории, дате, типу
- Добавление новых бронирований

## 🔗 Интеграция со Студентом A

Студент A (Booking Service) будет отправлять запросы на `/api/check-availability/` для проверки доступности.

**Пример интеграции:**
1. Студент A получает запрос на бронирование
2. Отправляет POST запрос на этот сервис
3. Получает ответ с результатом проверки
4. Создаёт или отклоняет бронирование

## 📝 Правила бронирования

- **Рабочее время**: 08:00 - 20:00 (по умолчанию)
- **Экзамены**: минимум 2 часа
- **Собрания**: максимум 4 часа
- **Занятия**: начало с 08:00 до 18:00

## 🎯 Демонстрация работы

1. Откройте веб-интерфейс
2. Создайте несколько аудиторий через админку или API
3. Добавьте тестовые бронирования
4. Проверьте доступность через форму
5. Проверьте API endpoints

## 📄 Лицензия

Учебный проект

## 👨‍💻 Автор

Студент B - Сервис проверки доступности