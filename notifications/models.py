from typing import Optional
from django.db import models
from django.utils import timezone

NULLABLE = {'null': True, 'blank': True}


class Notification(models.Model):
    """
    Модель уведомления.
    """
    DELAY_CHOICES = [
        (0, 'Без задержки'),
        (1, '1 час'),
        (2, '1 день'),
    ]

    message = models.TextField(
        max_length=1024,
        verbose_name="Сообщение",
        help_text="Текст уведомления, которое будет отправлено"
    )
    delay = models.PositiveSmallIntegerField(
        default=0,
        choices=DELAY_CHOICES,
        verbose_name="Задержка",
        help_text="Задержка перед отправкой уведомления"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
        help_text="Дата и время создания уведомления"
    )

    def __str__(self):
        return f"Уведомление #{self.id} от {self.created_at}"

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ["-created_at"]


class Recipient(models.Model):
    """
    Модель получателя уведомления.
    """
    EMAIL = "email"
    TELEGRAM = "telegram"
    RECEPIENT_TYPE_CHOICES = [
        (EMAIL, "Email"),
        (TELEGRAM, "Telegram"),
    ]

    notification = models.ForeignKey(
        Notification,
        related_name='recipients',
        on_delete=models.CASCADE,
        verbose_name="Уведомление"
    )
    recepient = models.CharField(
        max_length=150,
        verbose_name="Получатель",
        help_text="Email или ID Telegram"
    )
    recepient_type = models.CharField(
        max_length=50,
        choices=RECEPIENT_TYPE_CHOICES,
        verbose_name="Тип получателя",
        help_text="Тип получателя (Email или Telegram)"
    )

    def __str__(self):
        return f"Получатель {self.recepient} ({self.recepient_type}) для уведомления #{self.notification.id}"

    class Meta:
        verbose_name = "Получатель уведомления"
        verbose_name_plural = "Получатели уведомлений"


class NotificationSendLog(models.Model):
    """
    Модель для логирования попыток отправки уведомлений.

    Поля:
        - notification: связь с уведомлением, для которого делалась попытка отправки.
        - recipient: адрес или ID получателя уведомления.
        - recipient_type: тип получателя (email или telegram).
        - status: статус отправки уведомления ('успешно' или 'ошибка').
        - error_message: текст ошибки, если отправка не удалась.
        - timestamp: время попытки отправки.
    """

    STATUS_CHOICES = [
        ('Ok', 'Ok'),
        ('Error', 'Error'),
    ]

    notification: Notification = models.ForeignKey(
        'Notification', on_delete=models.CASCADE,
        verbose_name="Уведомление"
    )
    recipient: str = models.CharField(
        max_length=150,
        verbose_name="Получатель",
        help_text="Email или номер телефона получателя"
    )
    recipient_type: str = models.CharField(
        max_length=50,
        choices=[('email', 'Email'), ('telegram', 'Telegram')],
        verbose_name="Тип получателя",
        help_text="Тип получателя (Email или телефон)"
    )
    status: str = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        verbose_name="Статус",
        help_text="Статус отправки уведомления"
    )
    error_message: Optional[str] = models.TextField(
        **NULLABLE,
        verbose_name="Сообщение об ошибке",
        help_text="Текст ошибки, если отправка не удалась"
    )
    timestamp: models.DateTimeField = models.DateTimeField(
        default=timezone.now,
        verbose_name="Время попытки отправки",
        help_text="Дата и время попытки отправки уведомления"
    )

    def __str__(self) -> str:
        return f"{self.recipient} - {self.status} - {self.timestamp}"

    class Meta:
        verbose_name = 'Лог отправки уведомления'
        verbose_name_plural = 'Логи отправки уведомлений'
        ordering = ['-timestamp']
