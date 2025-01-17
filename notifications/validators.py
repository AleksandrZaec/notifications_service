import re
from rest_framework.exceptions import ValidationError
from rest_framework.fields import ListField, CharField


class StrictListField(ListField):
    """Кастомное поле, которое проверяет, что это список строк."""

    def to_internal_value(self, data):
        if not isinstance(data, list):
            raise ValidationError("Поле должно быть списком.")
        for item in data:
            if not isinstance(item, str):
                raise ValidationError(f"Элемент списка '{item}' должен быть строкой.")
        return super().to_internal_value(data)


def validate_unique_recipients(value):
    """Проверка на уникальность значений в списке."""
    if len(value) != len(set(value)):
        raise ValidationError("Получатели должны быть уникальными.")
    return value


def validate_email(value):
    """Проверка на правильность формата email."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, value):
        raise ValidationError(f"Неверный формат получателя: {value}")
    return value


def validate_telegram(value):
    """Проверка, что это только цифры для Телеграма."""
    if not value.isdigit():
        raise ValidationError(f"Неверный формат получателя: {value}")
    return value


def validate_recipients_format(value):
    """Проверка всех получателей на корректность формата (почта или Телеграм)."""
    if not isinstance(value, list):
        raise ValidationError("Поле 'recepient' должно быть списком строк.")
    for recepient in value:
        if not isinstance(recepient, str):
            raise ValidationError(f"Элемент списка '{recepient}' должен быть строкой.")
        if '@' in recepient:
            validate_email(recepient)
        else:
            validate_telegram(recepient)
    return value
