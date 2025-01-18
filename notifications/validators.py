import re
from rest_framework.exceptions import ValidationError
from rest_framework.fields import ListField
from typing import List


class StrictListField(ListField):
    """Кастомное поле, которое проверяет, что это список строк."""

    def to_internal_value(self, data: List[str]) -> List[str]:
        if not isinstance(data, list):
            raise ValidationError("Поле должно быть списком.")

        for item in data:
            if not isinstance(item, str):
                raise ValidationError(f"Элемент списка '{item}' должен быть строкой.")
            if not item:
                raise ValidationError(f"Элемент списка не может быть пустым или None.")

        return super().to_internal_value(data)


def validate_unique_recipients(value: List[str]) -> List[str]:
    """Проверка на уникальность значений в списке."""
    if len(value) != len(set(value)):
        raise ValidationError("Получатели должны быть уникальными.")
    return value


def validate_email(value: str) -> str:
    """Проверка на правильность формата email."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, value):
        raise ValidationError(f"Неверный формат получателя: {value}")
    return value


def validate_telegram(value: str) -> str:
    """Проверка, что это только цифры для Телеграма."""
    if not value.isdigit():
        raise ValidationError(f"Неверный формат получателя: {value}")
    return value
