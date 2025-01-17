import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Создание суперпользователя"

    def handle(self, *args, **kwargs):
        username = os.getenv("NOTIFICATIONS_SUPERUSER", "admin")
        password = os.getenv("NOTIFICATIONS_SUPERUSER_PASSWORD", "admin")

        if not username or not password:
            self.stdout.write(self.style.ERROR("Ошибка: Переменные окружения для суперпользователя не заданы."))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"Предупреждение: Суперпользователь '{username}' уже существует."))
        else:
            User.objects.create_superuser(username=username, email=None, password=password)
            self.stdout.write(self.style.SUCCESS(f"Суперпользователь '{username}' успешно создан."))
