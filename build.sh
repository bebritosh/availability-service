set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Создать суперпользователя, если его нет
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'Admin123456');
    print('✅ Суперпользователь создан')
else:
    print('ℹ️ Суперпользователь уже существует')
"
```

Потом сделайте commit и push - сервис пересоберётся.