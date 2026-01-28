// Availability Service - Student B - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const checkForm = document.getElementById('checkForm');
    if (checkForm) {
        checkForm.addEventListener('submit', function(e) {
            const startTime = document.getElementById('start_time').value;
            const endTime = document.getElementById('end_time').value;

            if (startTime && endTime && startTime >= endTime) {
                e.preventDefault();
                alert('Время начала должно быть раньше времени окончания!');
                return false;
            }
        });

        // Set minimum date to today
        const dateInput = document.getElementById('booking_date');
        if (dateInput) {
            const today = new Date().toISOString().split('T')[0];
            dateInput.setAttribute('min', today);
        }
    }

    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.alert');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.transition = 'opacity 0.5s';
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000);
    });

    // Confirm delete
    const deleteForms = document.querySelectorAll('form[action*="delete"]');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('Вы уверены, что хотите удалить это бронирование?')) {
                e.preventDefault();
                return false;
            }
        });
    });
});