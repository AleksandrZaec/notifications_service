from typing import Dict, List, Any
from rest_framework import serializers
from .models import Notification, Recipient
from .validators import StrictListField, validate_unique_recipients, validate_recipients_format
from rest_framework.exceptions import ValidationError


class CreateNotificationSerializer(serializers.Serializer):
    message: str
    recepient: List[str]
    delay: int
    message = serializers.CharField(max_length=1024)
    recepient = StrictListField(
        child=serializers.CharField(max_length=150),
        allow_empty=False,
        validators=[validate_unique_recipients, validate_recipients_format]
    )
    delay = serializers.ChoiceField(
        choices=[(0, 'Без задержки'), (1, '1 час'), (2, '1 день')],
        default=0
    )

    def to_internal_value(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Преобразуем поле 'recepient' в список, если это строка."""
        recepient = data.get('recepient')
        if isinstance(recepient, str):
            data['recepient'] = [recepient]
        elif not isinstance(recepient, list):
            raise ValidationError({"recepient": "Поле 'recepient' должно быть строкой или списком строк."})
        return super().to_internal_value(data)

    def create(self, validated_data: Dict[str, Any]) -> Notification:
        """Создание уведомления и добавление получателей в БД."""
        message = validated_data['message']
        delay = validated_data['delay']
        recepient_data = validated_data['recepient']

        notification = Notification.objects.create(message=message, delay=delay)

        for recepient in recepient_data:
            recipient_type = 'email' if '@' in recepient else 'telegram'
            Recipient.objects.create(notification=notification, recepient=recepient, recepient_type=recipient_type)

        return notification
