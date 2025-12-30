from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from catalog.models import Product
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem

User = get_user_model()


class OrderModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="12345"
        )

        self.product1 = Product.objects.create(
            name="Букет 1",
            price=1000
        )
        self.product2 = Product.objects.create(
            name="Букет 2",
            price=2000
        )

        self.order = Order.objects.create(user=self.user)

        OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            quantity=2
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product2,
            quantity=1
        )

    def test_order_item_total(self):
        item = self.order.items.first()
        self.assertEqual(item.total, item.product.price * item.quantity)

    def test_order_total_price(self):
        self.assertEqual(self.order.total_price, 4000)

    def test_order_str(self):
        self.assertIn("Заказ", str(self.order))


class OrderViewsTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="orderuser",
            password="12345"
        )
        self.client.login(username="orderuser", password="12345")

        self.product = Product.objects.create(
            name="Розы",
            price=2000
        )

        self.cart = self.user.cart

    def test_checkout_creates_order(self):
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )

        self.client.post(
            reverse("orders:checkout"),
            {
                "address": "Москва",
                "comment": "Позвонить заранее"
            }
        )

        order = Order.objects.get(user=self.user)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_price, 4000)

    def test_cart_is_cleared_after_checkout(self):
        self.client.post(
            reverse("orders:checkout"),
            {"address": "Москва"}
        )

        self.assertEqual(self.cart.items.count(), 0)

    def test_repeat_order(self):
        order = Order.objects.create(user=self.user)

        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=3
        )

        self.client.get(
            reverse("orders:repeat_order", args=[order.id])
        )

        cart_item = CartItem.objects.get(cart=self.cart)
        self.assertEqual(cart_item.quantity, 3)

    def test_cancel_order(self):
        order = Order.objects.create(user=self.user, status="new")

        self.client.get(
            reverse("orders:cancel_order", args=[order.id])
        )

        order.refresh_from_db()
        self.assertEqual(order.status, "canceled")

    def test_user_cannot_cancel_foreign_order(self):
        other_user = User.objects.create_user(
            username="hacker",
            password="12345"
        )
        order = Order.objects.create(user=other_user)

        response = self.client.get(
            reverse("orders:cancel_order", args=[order.id])
        )

        self.assertEqual(response.status_code, 404)
