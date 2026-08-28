import requests
from django.conf import settings


def send_telegram_message(text: str):

    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = str(settings.TELEGRAM_ADMIN_CHAT_ID).replace(" ", "")

    if not token:
        print("❌ TELEGRAM_BOT_TOKEN не указан")
        return False

    if not chat_id:
        print("❌ TELEGRAM_ADMIN_CHAT_ID не указан")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    try:

        response = requests.post(
            url,
            data=payload,
            timeout=10
        )

        print("📡 Telegram HTTP:", response.status_code)
        print("📨 Telegram response:", response.text)

        if response.ok:
            print("✅ Telegram сообщение отправлено")
            return True

        print("❌ Telegram не принял сообщение")
        return False

    except requests.RequestException as e:

        print("❌ Ошибка соединения с Telegram:")
        print(e)

        return False