from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from notifications.serializers import CreateNotificationSerializer
from notifications.tasks import send_email_notifications_task, send_telegram_notification_task
from drf_yasg.utils import swagger_auto_schema
from typing import Any, List


class NotificationViewSet(viewsets.ViewSet):
    """
    ViewSet для создания уведомлений.
    """
    http_method_names: List[str] = ['post']

    @swagger_auto_schema(
        request_body=CreateNotificationSerializer,
        responses={201: 'Успех', 400: 'Ошибка'}
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Метод для создания уведомления.
        """
        serializer = CreateNotificationSerializer(data=request.data)

        if serializer.is_valid():
            notification = serializer.save()

            recipients = notification.recipients.all().values('recepient', 'recepient_type')

            delay = notification.delay
            delay_seconds = settings.DELAY_MAPPING.get(delay, 0)

            send_email_notifications_task.apply_async(args=[notification.id, delay_seconds], countdown=delay_seconds)
            send_telegram_notification_task.apply_async(args=[notification.id, delay_seconds], countdown=delay_seconds)

            return Response({
                'id': notification.id,
                'message': notification.message,
                'delay': notification.delay,
                'created_at': notification.created_at,
                'recipients': list(recipients)
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)