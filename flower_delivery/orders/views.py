from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .cart import Cart
from .models import Order, OrderItem
from .forms import CheckoutForm


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
    cart = Cart(request)

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(user=request.user)

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    quantity=item["quantity"]
                )

            cart.clear()
            return redirect("orders_list")
    else:
        form = CheckoutForm()

    return render(request, "orders/checkout.html", {"cart": cart, "form": form})


@login_required
def orders_list(request):
    orders = request.user.orders.all().order_by("-created_at")
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, "orders/order_detail.html", {"order": order})
