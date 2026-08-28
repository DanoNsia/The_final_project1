from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings

from .cart import Cart
from .models import Order, OrderItem
from .forms import CheckoutForm
from .telegram_utils import send_telegram_message

from cart.models import CartItem


@login_required
def cart_view(request):

    cart = Cart(request)

    return render(
        request,
        "orders/cart.html",
        {
            "cart": cart
        }
    )


@login_required
def add_to_cart(request, product_id):

    cart = Cart(request)

    cart.add(product_id)

    return redirect("cart:cart_view")


@login_required
def remove_from_cart(request, product_id):

    cart = Cart(request)

    cart.remove(product_id)

    return redirect("cart:cart_view")


@login_required
def checkout(request):

    cart = request.user.cart

    # Нельзя оформить пустую корзину
    if not cart.items.exists():

        return redirect("cart:cart_view")


    if request.method == "POST":

        form = CheckoutForm(request.POST)

        if form.is_valid():

            # ==============================
            # СОЗДАЁМ ЗАКАЗ
            # ==============================

            order = Order.objects.create(

                user=request.user,

                phone=form.cleaned_data["phone"],

                address=form.cleaned_data["address"],

                comment=form.cleaned_data.get(
                    "comment",
                    ""
                ),

                status="new"
            )


            # ==============================
            # ДОБАВЛЯЕМ ТОВАРЫ
            # ==============================

            for item in cart.items.all():

                OrderItem.objects.create(

                    order=order,

                    product=item.product,

                    quantity=item.quantity
                )


            # ==============================
            # ОТПРАВЛЯЕМ УВЕДОМЛЕНИЕ
            # ==============================

            send_order_notification(order)


            # ==============================
            # ОЧИЩАЕМ КОРЗИНУ
            # ==============================

            cart.items.all().delete()


            # ==============================
            # ПЕРЕХОДИМ К ЗАКАЗУ
            # ==============================

            return redirect(
                "orders:payment",
                order_id=order.id
            )


    else:

        form = CheckoutForm(

            initial={
                "phone": getattr(
                    request.user,
                    "phone",
                    ""
                )
            }
        )


    return render(
        request,
        "orders/checkout.html",
        {
            "cart": cart,
            "form": form
        }
    )

@login_required
def payment(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    # Если заказ уже оплачен,
    # повторно сообщать об оплате не нужно
    if order.payment_status == "paid":
        return redirect(
            "orders:order_detail",
            order_id=order.id
        )

    if request.method == "POST":

        order.payment_status = "checking"
        order.save(update_fields=["payment_status"])

        send_payment_notification(order)

        return redirect(
            "orders:order_detail",
            order_id=order.id
        )

    return render(
        request,
        "orders/payment.html",
        {
            "order": order,
            "payment_phone": settings.PAYMENT_PHONE,
            "payment_bank": settings.PAYMENT_BANK,
            "payment_recipient": settings.PAYMENT_RECIPIENT,
        }
    )

def send_payment_notification(order):

    message = f"""
💰 ПОКУПАТЕЛЬ СООБЩИЛ ОБ ОПЛАТЕ

Заказ №{order.id}

Клиент:
{order.user.username}

Телефон:
{order.phone}

Сумма:
{order.total_price} ₽

Статус оплаты:
Проверка оплаты

Необходимо проверить поступление денежных средств.
"""

    send_mail(
        subject=f"💰 Оплата заказа №{order.id} — Дари Цветы",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[
            settings.ORDER_NOTIFICATION_EMAIL
        ],
        fail_silently=True,
    )

    # Уведомление в Telegram
    telegram_message = (
        f"💰 <b>ПОКУПАТЕЛЬ СООБЩИЛ ОБ ОПЛАТЕ</b>\n\n"
        f"Заказ №{order.id}\n\n"
        f"👤 Клиент: {order.user.username}\n"
        f"📞 Телефон: {order.phone}\n"
        f"💰 Сумма: {order.total_price} ₽\n\n"
        f"🟡 <b>Статус оплаты: проверка</b>\n\n"
        f"Необходимо проверить поступление денег."
    )

# ==========================================================
# УВЕДОМЛЕНИЕ О НОВОМ ЗАКАЗЕ
# ==========================================================

def send_order_notification(order):

    products_text = ""

    for item in order.items.all():

        products_text += (
            f"- {item.product.name} "
            f"x {item.quantity} — "
            f"{item.total} ₽\n"
        )

    message = f"""
Новый заказ №{order.id}

Клиент:
{order.user.username}

Телефон:
{order.phone}

Адрес доставки:
{order.address}

Комментарий:
{order.comment or "Не указан"}

Товары:
{products_text}

Итого:
{order.total_price} ₽

Статус:
Новый
"""

    # EMAIL
    send_mail(
        subject=f"🌷 Новый заказ №{order.id} — Дари Цветы",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[
            settings.ORDER_NOTIFICATION_EMAIL
        ],
        fail_silently=True,
    )

    # TELEGRAM
    telegram_message = (
        f"🌷 <b>НОВЫЙ ЗАКАЗ #{order.id}</b>\n\n"
        f"👤 <b>Клиент:</b> {order.user.username}\n"
        f"📞 <b>Телефон:</b> {order.phone}\n"
        f"📍 <b>Адрес:</b> {order.address}\n"
        f"💬 <b>Комментарий:</b> "
        f"{order.comment or 'Не указан'}\n\n"
        f"🛒 <b>Товары:</b>\n"
        f"{products_text}\n"
        f"💰 <b>Итого:</b> {order.total_price} ₽\n"
        f"📌 <b>Статус:</b> Новый"
    )

    send_telegram_message(telegram_message)

# ==========================================================
# МОИ ЗАКАЗЫ
# ==========================================================

@login_required
def orders_list(request):

    orders = request.user.orders.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "orders/order_list.html",
        {
            "orders": orders
        }
    )


# ==========================================================
# ПОДРОБНОСТИ ЗАКАЗА
# ==========================================================

@login_required
def order_detail(request, order_id):

    order = get_object_or_404(

        Order,

        id=order_id,

        user=request.user
    )

    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order
        }
    )


# ==========================================================
# ОТМЕНА ЗАКАЗА
# ==========================================================

@login_required
def cancel_order(request, order_id):

    order = get_object_or_404(

        Order,

        id=order_id,

        user=request.user
    )


    # Отменить можно только новый заказ

    if order.status == "new":

        order.status = "canceled"

        order.save()


    return redirect(
        "orders:order_detail",
        order_id=order.id
    )


# ==========================================================
# ПОВТОР ЗАКАЗА
# ==========================================================

@login_required
def repeat_order(request, order_id):

    order = get_object_or_404(

        Order,

        id=order_id,

        user=request.user
    )

    cart = request.user.cart


    # Очищаем текущую корзину

    cart.items.all().delete()


    # Добавляем товары из старого заказа

    for item in order.items.all():

        CartItem.objects.create(

            cart=cart,

            product=item.product,

            quantity=item.quantity
        )


    return redirect(
        "cart:cart_view"
    )