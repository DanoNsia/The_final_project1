import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flower_delivery.settings")
django.setup()

from telegram.ext import Updater, CommandHandler
from orders.models import Order
from django.conf import settings


def orders_command(update, context):
    """
    /orders — последние 5 заказов
    """

    if update.effective_user.id != int(settings.TELEGRAM_ADMIN_CHAT_ID):
        update.message.reply_text("❌ Нет доступа")
        return

    text = "📦 <b>Последние заказы:</b>\n\n"

    orders = Order.objects.exclude(status="draft").order_by("-created_at")[:5]

    if not orders:
        text += "Заказов пока нет"
    else:
        for order in orders:
            text += (
                f"#{order.id} — "
                f"{order.get_status_display()} — "
                f"{order.total_price} ₽\n"
            )

    update.message.reply_text(text, parse_mode="HTML")


def main():
    if not settings.TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN не задан")
        return

    updater = Updater(token=settings.TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("orders", orders_command))

    print("🤖 Telegram админ-бот запущен")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
