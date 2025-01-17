from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from notifications.serializers import CreateNotificationSerializer
from notifications.tasks import send_email_notifications_task, send_telegram_notification_task


class NotificationViewSet(viewsets.ViewSet):
    """
    ViewSet для создания уведомлений.
    """
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = CreateNotificationSerializer(data=request.data)

        if serializer.is_valid():
            notification = serializer.save()

            recipients = notification.recipients.all().values('recepient', 'recepient_type')

            delay = notification.delay
            delay_seconds = settings.DELAY_MAPPING.get(delay)

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
