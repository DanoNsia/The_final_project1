import os
import sys


# ==========================================================
# ПУТЬ К КОРНЮ ПРОЕКТА
# ==========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# ==========================================================
# DJANGO
# ==========================================================

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "flower_delivery.settings"
)

import django

django.setup()


# ==========================================================
# IMPORTS
# ==========================================================

from asgiref.sync import sync_to_async

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)

from django.conf import settings
from orders.models import Order


# ==========================================================
# ПРОВЕРКА АДМИНА
# ==========================================================

def is_admin(update: Update) -> bool:

    user = update.effective_user

    admin_chat_id = str(
        getattr(
            settings,
            "TELEGRAM_ADMIN_CHAT_ID",
            ""
        )
    ).strip()

    if not user:
        return False

    return str(user.id) == admin_chat_id


# ==========================================================
# ПОЛУЧЕНИЕ ПОСЛЕДНИХ ЗАКАЗОВ
# ==========================================================

@sync_to_async
def get_orders():

    return list(
        Order.objects
        .exclude(status="draft")
        .order_by("-created_at")[:5]
    )


# ==========================================================
# ПОЛУЧЕНИЕ ОДНОГО ЗАКАЗА
# ==========================================================

@sync_to_async
def get_order(order_id):

    try:

        return Order.objects.get(
            id=order_id
        )

    except Order.DoesNotExist:

        return None


# ==========================================================
# ИЗМЕНЕНИЕ СТАТУСА
# ==========================================================

@sync_to_async
def change_order_status(
    order_id,
    new_status
):

    try:

        order = Order.objects.get(
            id=order_id
        )

    except Order.DoesNotExist:

        return None

    order.status = new_status
    order.save(
        update_fields=["status"]
    )

    return order


# ==========================================================
# ФОРМИРОВАНИЕ ЗАКАЗА
# ==========================================================

@sync_to_async
def get_order_text(order_id):

    try:

        order = (
            Order.objects
            .prefetch_related(
                "items__product"
            )
            .get(id=order_id)
        )

    except Order.DoesNotExist:

        return None

    text = (
        f"🌷 <b>Заказ №{order.id}</b>\n\n"

        f"👤 <b>Клиент:</b>\n"
        f"{order.user.username}\n\n"

        f"📞 <b>Телефон:</b>\n"
        f"{order.phone}\n\n"

        f"📍 <b>Адрес:</b>\n"
        f"{order.address}\n\n"

        f"💬 <b>Комментарий:</b>\n"
        f"{order.comment or 'Не указан'}\n\n"

        f"🌸 <b>Товары:</b>\n"
    )

    for item in order.items.all():

        text += (
            f"• {item.product.name} "
            f"x {item.quantity} — "
            f"{item.total} ₽\n"
        )

    text += (
        f"\n💰 <b>Итого:</b> "
        f"{order.total_price} ₽\n\n"

        f"📊 <b>Статус:</b> "
        f"{order.get_status_display()}"
    )

    return text


# ==========================================================
# КНОПКИ ЗАКАЗА
# ==========================================================

def get_order_keyboard(order):

    keyboard = [

        [
            InlineKeyboardButton(
                "🔵 В обработку",
                callback_data=f"status:{order.id}:processing"
            )
        ],

        [
            InlineKeyboardButton(
                "🟢 Выполнен",
                callback_data=f"status:{order.id}:done"
            )
        ],

        [
            InlineKeyboardButton(
                "🔴 Отменить",
                callback_data=f"status:{order.id}:canceled"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Назад к заказам",
                callback_data="orders_list"
            )
        ]

    ]

    return InlineKeyboardMarkup(
        keyboard
    )


# ==========================================================
# КНОПКИ СПИСКА ЗАКАЗОВ
# ==========================================================

def get_orders_keyboard(orders):

    keyboard = []

    for order in orders:

        keyboard.append(

            [
                InlineKeyboardButton(
                    f"🌷 Заказ #{order.id} — "
                    f"{order.get_status_display()}",
                    callback_data=f"order:{order.id}"
                )
            ]

        )

    return InlineKeyboardMarkup(
        keyboard
    )


# ==========================================================
# /START
# ==========================================================

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_admin(update):

        await update.message.reply_text(
            "❌ У вас нет доступа к этому боту."
        )

        return

    keyboard = [

        [
            InlineKeyboardButton(
                "📦 Все заказы",
                callback_data="orders_list"
            )
        ]

    ]

    await update.message.reply_text(

        "🌷 <b>Бот магазина «Дари Цветы»</b>\n\n"

        "Бот подключён и работает.\n\n"

        "Выберите действие:",

        parse_mode="HTML",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


# ==========================================================
# /ORDERS
# ==========================================================

async def orders_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_admin(update):

        await update.message.reply_text(
            "❌ У вас нет доступа к этому боту."
        )

        return

    orders = await get_orders()

    if not orders:

        await update.message.reply_text(
            "📦 Заказов пока нет."
        )

        return

    text = (
        "📦 <b>Последние 5 заказов</b>\n\n"
        "Нажмите на заказ, чтобы открыть его:"
    )

    await update.message.reply_text(

        text,

        parse_mode="HTML",

        reply_markup=get_orders_keyboard(
            orders
        )
    )


# ==========================================================
# CALLBACK-КНОПКИ
# ==========================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user = query.from_user

    admin_chat_id = str(
        getattr(
            settings,
            "TELEGRAM_ADMIN_CHAT_ID",
            ""
        )
    ).strip()

    if str(user.id) != admin_chat_id:

        await query.answer(
            "❌ Нет доступа",
            show_alert=True
        )

        return

    data = query.data


    # ======================================================
    # СПИСОК ЗАКАЗОВ
    # ======================================================

    if data == "orders_list":

        orders = await get_orders()

        if not orders:

            await query.edit_message_text(
                "📦 Заказов пока нет."
            )

            return

        await query.edit_message_text(

            "📦 <b>Последние 5 заказов</b>\n\n"
            "Выберите заказ:",

            parse_mode="HTML",

            reply_markup=get_orders_keyboard(
                orders
            )
        )

        return


    # ======================================================
    # ОТКРЫТИЕ ЗАКАЗА
    # ======================================================

    if data.startswith("order:"):

        order_id = data.split(":")[1]

        order = await get_order(
            order_id
        )

        if not order:

            await query.edit_message_text(
                "❌ Заказ не найден."
            )

            return

        text = await get_order_text(
            order_id
        )

        await query.edit_message_text(

            text,

            parse_mode="HTML",

            reply_markup=get_order_keyboard(
                order
            )
        )

        return


    # ======================================================
    # ИЗМЕНЕНИЕ СТАТУСА
    # ======================================================

    if data.startswith("status:"):

        parts = data.split(":")

        order_id = parts[1]
        new_status = parts[2]

        order = await change_order_status(
            order_id,
            new_status
        )

        if not order:

            await query.edit_message_text(
                "❌ Заказ не найден."
            )

            return

        text = await get_order_text(
            order_id
        )

        await query.edit_message_text(

            text,

            parse_mode="HTML",

            reply_markup=get_order_keyboard(
                order
            )
        )

        return


# ==========================================================
# ОБРАБОТЧИК ОШИБОК
# ==========================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    print(
        "❌ Ошибка Telegram-бота:",
        context.error
    )


# ==========================================================
# ЗАПУСК
# ==========================================================

def main():

    token = str(
        getattr(
            settings,
            "TELEGRAM_BOT_TOKEN",
            ""
        )
    ).strip()

    if not token:

        print(
            "❌ TELEGRAM_BOT_TOKEN не задан"
        )

        return

    print(
        "🔄 Запуск Telegram-бота..."
    )

    application = (
        Application.builder()
        .token(token)
        .build()
    )


    # ======================================================
    # КОМАНДЫ
    # ======================================================

    application.add_handler(

        CommandHandler(
            "start",
            start_command
        )

    )

    application.add_handler(

        CommandHandler(
            "orders",
            orders_command
        )

    )


    # ======================================================
    # INLINE-КНОПКИ
    # ======================================================

    application.add_handler(

        CallbackQueryHandler(
            button_handler
        )

    )


    # ======================================================
    # ОШИБКИ
    # ======================================================

    application.add_error_handler(
        error_handler
    )


    print(
        "🤖 Telegram-бот запущен"
    )

    application.run_polling()


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    main()