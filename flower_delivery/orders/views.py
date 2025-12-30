from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .cart import Cart
from .models import Order, OrderItem
from .forms import CheckoutForm
from django.shortcuts import get_object_or_404
from cart.models import CartItem

@login_required
def cart_view(request):
    cart = Cart(request)
    return render(request, "orders/cart.html", {"cart": cart})


@login_required
def add_to_cart(request, product_id):
    cart = Cart(request)
    cart.add(product_id)
    return redirect("cart")


@login_required
def remove_from_cart(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    return redirect("cart")


@login_required
def checkout(request):
    cart = request.user.cart

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():

            # 1️⃣ создаём заказ как черновик
            order = Order.objects.create(
                user=request.user,
                address=form.cleaned_data["address"],
                comment=form.cleaned_data.get("comment", ""),
                status="draft"
            )

            # 2️⃣ добавляем товары
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )

            # 3️⃣ очищаем корзину
            cart.items.all().delete()

            # 4️⃣ ПОДТВЕРЖДАЕМ заказ (вот тут Telegram)
            order.status = "new"
            order.save()

            return redirect("orders:orders_list")
    else:
        form = CheckoutForm()

    return render(request, "orders/checkout.html", {
        "cart": cart,
        "form": form
    })



@login_required
def orders_list(request):
    orders = request.user.orders.all().order_by("-created_at")
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, "orders/order_detail.html", {"order": order})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    # отменять можно только новые заказы
    if order.status == "new":
        order.status = "canceled"
        order.save()

    return redirect("orders:order_detail", order_id=order.id)

@login_required
def repeat_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    cart = request.user.cart

    # 1️⃣ очищаем корзину
    cart.items.all().delete()

    # 2️⃣ копируем товары из заказа
    for item in order.items.all():
        CartItem.objects.create(
            cart=cart,
            product=item.product,
            quantity=item.quantity
        )

    return redirect("cart:cart_view")