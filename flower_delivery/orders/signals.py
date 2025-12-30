from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .telegram import send_telegram_message


@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    """
    Telegram-уведомление ТОЛЬКО когда заказ подтверждён (status = new)
    """

    if instance.status != "new":
        return

    # 🛒 Состав заказа
    items = instance.items.all()

    if not items.exists():
        return  # защита от пустых заказов

    total = 0
    items_text = ""

    for item in items:
        item_total = item.product.price * item.quantity
        total += item_total

        items_text += (
            f"• {item.product.name}\n"
            f"  Кол-во: {item.quantity}\n"
            f"  Цена: {item.product.price} ₽\n"
            f"  Сумма: {item_total} ₽\n\n"
        )

    user_name = instance.user.username if instance.user else "Гость"

    text = (
        f"🆕 <b>Новый заказ #{instance.id}</b>\n\n"
        f"👤 Пользователь: {user_name}\n"
        f"📍 Адрес: {instance.address}\n\n"
        f"🛒 <b>Состав заказа:</b>\n"
        f"{items_text}"
        f"💰 <b>Итого: {total} ₽</b>"
    )

    send_telegram_message(text)
