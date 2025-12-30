from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from catalog.models import Product


@login_required
def cart_view(request):
    cart = request.user.cart
    items = cart.items.all()        # правильное получение товаров
    total = sum(i.total for i in items)

    return render(request, "cart/cart.html", {
        "cart": cart,
        "items": items,
        "total": total,
    })



@login_required
def add_to_cart(request, product_id):
    cart = request.user.cart
    product = get_object_or_404(Product, id=product_id)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        item.quantity += 1

    item.save()

    return redirect("cart:cart_view")


@login_required
def remove_from_cart(request, item_id):
    cart = request.user.cart
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    return redirect("cart:cart_view")

@login_required
def increase_quantity(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=request.user.cart
    )
    item.quantity += 1
    item.save()
    return redirect("cart:cart_view")


@login_required
def decrease_quantity(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=request.user.cart
    )

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect("cart:cart_view")
