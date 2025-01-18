from typing import Dict, List, Any
from rest_framework import serializers
from .models import Notification, Recipient
from .validators import StrictListField, validate_unique_recipients, validate_email, validate_telegram
from rest_framework.exceptions import ValidationError


class CreateNotificationSerializer(serializers.Serializer):
    message: str
    recepient: List[str]
    delay: int

    message = serializers.CharField(max_length=1024)
    recepient = StrictListField(
        child=serializers.CharField(max_length=150),
        allow_empty=False,
        validators=[validate_unique_recipients]
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

    def validate_recepient(self, recepients: List[str]) -> List[Dict[str, str]]:
        """Валидация получателей в список."""
        invalid_recipients = []
        valid_recipients = []

        for recipient in recepients:
            try:
                if isinstance(recipient, str):
                    recipient_value = recipient
                elif isinstance(recipient, dict):
                    recipient_value = recipient.get("recipient", "")
                else:
                    raise ValidationError

                if '@' in recipient_value:
                    validate_email(recipient_value)
                    recipient_type = "email"
                else:
                    validate_telegram(recipient_value)
                    recipient_type = "telegram"

                valid_recipients.append({"recipient": recipient, "recipient_type": recipient_type})
            except ValidationError as e:
                invalid_recipients.append({"recipient": recipient, "error": "Некорректный получатель"})

        if invalid_recipients:
            raise ValidationError(invalid_recipients)

        return valid_recipients

    def create(self, validated_data: Dict[str, Any]) -> Notification:
        """Создание уведомления и добавление получателей в БД."""
        message = validated_data['message']
        delay = validated_data['delay']
        recepients = validated_data['recepient']

        prepared_recepients = self.validate_recepient(recepients)

        notification = Notification.objects.create(message=message, delay=delay)

        Recipient.objects.bulk_create([
            Recipient(
                notification=notification,
                recepient=recepient["recipient"],
                recepient_type=recepient["recipient_type"]
            )
            for recepient in prepared_recepients
        ])

        return notification
