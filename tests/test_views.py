import pytest
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch


@pytest.fixture
def api_client():
    """Фикстура для создания клиента API."""
    return APIClient()


@pytest.fixture
def create_notification_data_list():
    """Фикстура с данными, где `recepient` — список строк."""
    return {
        "message": "Test message",
        "recepient": ["test1@test.com", "123456789"],
        "delay": 0
    }


@pytest.fixture
def create_notification_data_string():
    """Фикстура с данными, где `recepient` — строка."""
    return {
        "message": "Test message",
        "recepient": "test@test.com",  # Строка вместо списка
        "delay": 0
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    "notification_data",
    [
        pytest.param(
            {"message": "Test message", "recepient": ["test1@test.com", "123456789"], "delay": 0},
            id="list_recepient",
        ),
        pytest.param(
            {"message": "Test message", "recepient": "test@test.com", "delay": 0},
            id="string_recepient",
        ),
    ],
)
def test_create_notification(api_client, notification_data):
    """Тест успешного создания уведомления для разных типов поля `recepient`."""
    url = '/api/notify/'

    response = api_client.post(url, data=notification_data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert 'id' in response.data
    assert 'message' in response.data
    assert response.data['message'] == notification_data['message']
    assert len(response.data['recipients']) == (
        1 if isinstance(notification_data['recepient'], str) else len(notification_data['recepient'])
    )


@pytest.mark.django_db
@patch('notifications.views.send_email_notifications_task.apply_async')
@patch('notifications.views.send_telegram_notification_task.apply_async')
def test_create_notification_with_task_call(
    mock_send_email, mock_send_telegram, api_client, create_notification_data_list
):
    """Тест успешного создания уведомления с вызовом задач."""
    url = '/api/notify/'

    response = api_client.post(url, data=create_notification_data_list, format='json')

    mock_send_email.assert_called_once()
    mock_send_telegram.assert_called_once()

    assert response.status_code == status.HTTP_201_CREATED
    assert 'id' in response.data
    assert response.data['message'] == create_notification_data_list['message']


@pytest.mark.django_db
@pytest.mark.parametrize(
    "invalid_data, expected_error_field",
    [
        pytest.param(
            {"message": "Test message", "recepient": 12345, "delay": 0},
            'recepient',
            id="invalid_type_int"
        ),
        pytest.param(
            {"message": "Test message", "recepient": [], "delay": 0},
            'recepient',
            id="empty_list"
        ),
        pytest.param(
            {"message": "Test message", "recepient": ["test1@test.com", 123456789], "delay": 0},
            'recepient',
            id="list_with_invalid_item"
        ),
        pytest.param(
            {"message": "Test message", "recepient": ["test1@test.com", []], "delay": 0},
            'recepient',
            id="list_with_empty_sublist"
        ),
        pytest.param(
            {"message": "Test message", "recepient": ["test1@test.com", ["123456789"]], "delay": 0},
            'recepient',
            id="list_with_sublist_as_recipient"
        ),
        pytest.param(
            {"message": "Test message", "recepient": ["test1test.com"], "delay": 0},
            'recepient',
            id="list_with_sublist_as_recipient"
        ),
        pytest.param(
            {"message": "Test message", "recepient": ["test1@test.com", "test1@test.com"], "delay": 0},
            'recepient',
            id="list_with_sublist_as_recipient"
        ),
    ],
)
def test_create_notification_invalid_data(api_client, invalid_data, expected_error_field):
    """Тест с некорректными данными для разных вариантов поля `recepient`."""
    url = '/api/notify/'

    response = api_client.post(url, data=invalid_data, format='json')
    print(response.status_code)  # Печать статуса
    print(response.data)  # Печать данных
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert expected_error_field in response.data


@pytest.mark.django_db
def test_create_notification_missing_field(api_client):
    """Тест с отсутствующим обязательным полем."""
    url = '/api/notify/'

    missing_field_data = {
        "message": "Test message",
        "delay": 0
    }

    response = api_client.post(url, data=missing_field_data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'recepient' in response.data
