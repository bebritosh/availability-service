from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView
from datetime import date, datetime

from .models import Room, RoomSchedule, WorkingHours
from .services import AvailabilityChecker


class HomeView(View):
    """
    Главная страница с проверкой доступности
    """

    def get(self, request):
        rooms = Room.objects.filter(is_active=True)
        recent_checks = RoomSchedule.objects.all()[:10]

        context = {
            'rooms': rooms,
            'recent_checks': recent_checks,
            'today': date.today(),
        }
        return render(request, 'availability/home.html', context)

    def post(self, request):
        """Обработка проверки доступности"""
        try:
            check_data = {
                'room_number': request.POST.get('room_number'),
                'booking_date': datetime.strptime(
                    request.POST.get('booking_date'), '%Y-%m-%d'
                ).date(),
                'start_time': datetime.strptime(
                    request.POST.get('start_time'), '%H:%M'
                ).time(),
                'end_time': datetime.strptime(
                    request.POST.get('end_time'), '%H:%M'
                ).time(),
                'booking_type': request.POST.get('booking_type', 'lesson'),
            }

            checker = AvailabilityChecker()
            result = checker.check_availability(check_data)

            if result['available']:
                messages.success(
                    request,
                    f'✅ {result["message"]}'
                )
            else:
                conflicts_text = '\n'.join(result.get('conflicts', []))
                messages.warning(
                    request,
                    f'❌ {result["message"]}\n{conflicts_text}'
                )

            # Сохраняем результат проверки для истории
            request.session['last_check'] = {
                'room_number': check_data['room_number'],
                'booking_date': str(check_data['booking_date']),
                'start_time': str(check_data['start_time']),
                'end_time': str(check_data['end_time']),
                'result': result
            }

            return redirect('home')

        except Exception as e:
            messages.error(request, f'Ошибка при проверке доступности: {str(e)}')
            return redirect('home')


class RoomListView(ListView):
    """
    Список всех аудиторий
    """
    model = Room
    template_name = 'availability/room_list.html'
    context_object_name = 'rooms'
    paginate_by = 20

    def get_queryset(self):
        queryset = Room.objects.all()

        # Фильтрация по активности
        is_active = self.request.GET.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=(is_active == 'true'))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_rooms'] = Room.objects.count()
        context['active_rooms'] = Room.objects.filter(is_active=True).count()
        return context


class RoomDetailView(DetailView):
    """
    Детальная информация об аудитории
    """
    model = Room
    template_name = 'availability/room_detail.html'
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = self.object

        # Получаем расписание аудитории
        today = date.today()
        context['schedule'] = RoomSchedule.objects.filter(
            room_number=room.number,
            booking_date__gte=today
        ).order_by('booking_date', 'start_time')[:20]

        # Получаем рабочие часы
        context['working_hours'] = WorkingHours.objects.filter(
            room_number=room.number
        ).order_by('weekday')

        return context


class ScheduleListView(ListView):
    """
    Список всех бронирований
    """
    model = RoomSchedule
    template_name = 'availability/shedule_list.html'
    context_object_name = 'schedules'
    paginate_by = 50

    def get_queryset(self):
        queryset = RoomSchedule.objects.all()

        # Фильтрация по аудитории
        room_number = self.request.GET.get('room')
        if room_number:
            queryset = queryset.filter(room_number=room_number)

        # Фильтрация по дате
        booking_date = self.request.GET.get('date')
        if booking_date:
            queryset = queryset.filter(booking_date=booking_date)

        # Фильтрация по типу
        booking_type = self.request.GET.get('type')
        if booking_type:
            queryset = queryset.filter(booking_type=booking_type)

        return queryset.order_by('-booking_date', '-start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_bookings'] = RoomSchedule.objects.count()
        context['rooms'] = Room.objects.filter(is_active=True).values_list('number', flat=True)
        return context


class ScheduleDetailView(DetailView):
    """
    Детальная информация о бронировании
    """
    model = RoomSchedule
    template_name = 'availability/schedule_detail.html'
    context_object_name = 'schedule'


class AddScheduleView(View):
    """
    Добавление нового бронирования в расписание
    """

    def get(self, request):
        rooms = Room.objects.filter(is_active=True)
        context = {
            'rooms': rooms,
            'today': date.today(),
        }
        return render(request, 'availability/add_schedule.html', context)

    def post(self, request):
        try:
            schedule_data = {
                'room_number': request.POST.get('room_number'),
                'booking_date': request.POST.get('booking_date'),
                'start_time': request.POST.get('start_time'),
                'end_time': request.POST.get('end_time'),
                'booking_type': request.POST.get('booking_type'),
                'description': request.POST.get('description', ''),
                'booked_by': request.POST.get('booked_by'),
            }

            schedule = RoomSchedule.objects.create(**schedule_data)

            messages.success(
                request,
                f'✅ Бронирование успешно добавлено в расписание!'
            )
            return redirect('schedule_detail', pk=schedule.pk)

        except Exception as e:
            messages.error(request, f'Ошибка при создании бронирования: {str(e)}')
            return redirect('add_schedule')


class DeleteScheduleView(View):
    """
    Удаление бронирования
    """

    def post(self, request, pk):
        schedule = get_object_or_404(RoomSchedule, pk=pk)
        room_number = schedule.room_number
        schedule.delete()

        messages.success(
            request,
            f'Бронирование аудитории {room_number} успешно удалено'
        )
        return redirect('schedule_list')