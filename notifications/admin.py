from django.contrib import admin
from django.utils.timezone import localtime
from typing import Any
from .models import Notification, Recipient, NotificationSendLog


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Notification.
    Отображает список уведомлений, позволяет фильтровать и искать.
    """
    list_display = ['id', 'message', 'delay', 'created_at_local']
    search_fields = ['id', 'message']
    list_filter = ['delay', 'created_at']
    ordering = ['-created_at']
    list_per_page = 20

    def created_at_local(self, obj: Notification) -> str:
        return localtime(obj.created_at).strftime("%d.%m.%Y %H:%M:%S")


setattr(NotificationAdmin.created_at_local, 'short_description', "Дата создания")


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Recipient.
    Отображает информацию о получателях уведомлений.
    """
    list_display = ['id', 'recepient', 'recepient_type', 'notification_display']
    search_fields = ['recepient', 'recepient_type', 'notification__id']
    list_filter = ['recepient_type']
    ordering = ['notification']
    list_per_page = 20

    def notification_display(self, obj: Recipient) -> str:
        return f"Уведомление #{obj.notification.id} от {localtime(obj.notification.created_at).strftime('%d.%m.%Y %H:%M:%S')}"


setattr(RecipientAdmin.notification_display, 'short_description', "Уведомление")


@admin.register(NotificationSendLog)
class NotificationSendLogAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели NotificationSendLog.
    Отображает информацию о логах отправки уведомлений.
    """
    list_display = ['id', 'recipient', 'status', 'timestamp_local', 'notification_display', 'error_message']
    search_fields = ['recipient', 'status', 'notification__id']
    list_filter = ['status', 'timestamp']
    ordering = ['-timestamp']
    list_per_page = 20

    def timestamp_local(self, obj: NotificationSendLog) -> str:
        return localtime(obj.timestamp).strftime("%d.%m.%Y %H:%M:%S")

    def notification_display(self, obj: NotificationSendLog) -> str:
        return f"Уведомление #{obj.notification.id} от {localtime(obj.notification.created_at).strftime('%d.%m.%Y %H:%M:%S')}"


setattr(NotificationSendLogAdmin.timestamp_local, 'short_description', "Дата отправки")
setattr(NotificationSendLogAdmin.notification_display, 'short_description', "Уведомление")
