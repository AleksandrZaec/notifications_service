import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def send_telegram_message(chat_id: str, message: str) -> requests.Response:
    """Отправка сообщения в Telegram с использованием бота."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": message
    }
    response: requests.Response = requests.get(url, params=params)
    return response
