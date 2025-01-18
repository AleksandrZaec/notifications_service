from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from config.settings import EMAIL_HOST_USER
from notifications.models import Notification, NotificationSendLog, Recipient
from notifications.services import send_telegram_message


@shared_task
def send_email_to_recipient_task(notification_id: int, recipient_email: str) -> None:
    """
    Задача для отправки email одному получателю с учетом задержки.
    """
    try:
        notification = Notification.objects.get(id=notification_id)

        send_mail(
            subject="Новое уведомление",
            message=notification.message,
            from_email=EMAIL_HOST_USER,
            recipient_list=[recipient_email],
            fail_silently=False
        )

        NotificationSendLog.objects.create(
            notification=notification,
            recipient=recipient_email,
            recipient_type='email',
            status='Ok',
            timestamp=timezone.now()
        )
    except Exception as e:
        NotificationSendLog.objects.create(
            notification=notification,
            recipient=recipient_email,
            recipient_type='email',
            status='Error',
            error_message=str(e),
            timestamp=timezone.now()
        )
        print(f"Ошибка отправки email для {recipient_email}: {e}")


@shared_task
def send_email_notifications_task(notification_id: int, delay_seconds: int) -> None:
    """
    Задача для запуска задач отправки email для всех получателей.
    """
    recipients_email = Recipient.objects.filter(notification_id=notification_id, recepient_type='email')

    for recipient in recipients_email:
        send_email_to_recipient_task.apply_async(
            args=[notification_id, recipient.recepient],
            countdown=delay_seconds
        )


@shared_task
def send_telegram_to_recipient_task(notification_id: int, recipient_telegram: str) -> None:
    """
    Задача для отправки Telegram сообщения одному получателю.
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        response = send_telegram_message(recipient_telegram, notification.message)

        if response.status_code == 200:
            NotificationSendLog.objects.create(
                notification=notification,
                recipient=recipient_telegram,
                recipient_type='telegram',
                status='Ok',
                timestamp=timezone.now()
            )
        else:
            raise Exception(f"Ошибка Telegram API, код ответа: {response.status_code}")

    except Exception as e:
        NotificationSendLog.objects.create(
            notification=notification,
            recipient=recipient_telegram,
            recipient_type='telegram',
            status='Error',
            error_message=str(e),
            timestamp=timezone.now()
        )
        print(f"Ошибка отправки в Telegram: {e}")


@shared_task
def send_telegram_notification_task(notification_id: int, delay_seconds: int) -> None:
    """
    Задача для запуска задач отправки Telegram сообщений для всех получателей.
    """
    recipients_telegram = Recipient.objects.filter(notification_id=notification_id, recepient_type='telegram')
    for recipient in recipients_telegram:
        send_telegram_to_recipient_task.apply_async(
            args=[notification_id, recipient.recepient],
            countdown=delay_seconds
        )
