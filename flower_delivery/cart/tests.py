from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from catalog.models import Product
from cart.models import CartItem

User = get_user_model()


class CartModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="cartuser",
            password="12345"
        )

        self.cart = self.user.cart  # 👈 ВАЖНО

        self.product = Product.objects.create(
            name="Розы",
            price=1500
        )

        self.item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=3
        )

    def test_cart_item_total(self):
        self.assertEqual(self.item.total, 4500)

    def test_cart_total_price(self):
        self.assertEqual(self.cart.total_price, 4500)


class CartViewsTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="cartuser",
            password="12345"
        )
        self.client.login(username="cartuser", password="12345")

        self.product = Product.objects.create(
            name="Букет",
            price=1000
        )

        self.cart = self.user.cart  # 👈 ВАЖНО

    def test_add_to_cart(self):
        self.client.get(
            reverse("cart:add_to_cart", args=[self.product.id])
        )

        item = CartItem.objects.get(cart=self.cart)
        self.assertEqual(item.quantity, 1)

    def test_increase_quantity(self):
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )

        self.client.get(
            reverse("cart:increase", args=[item.id])
        )

        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)

    def test_decrease_quantity(self):
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )

        self.client.get(
            reverse("cart:decrease", args=[item.id])
        )

        item.refresh_from_db()
        self.assertEqual(item.quantity, 1)

    def test_remove_from_cart(self):
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )

        self.client.get(
            reverse("cart:remove_from_cart", args=[item.id])
        )

        self.assertFalse(CartItem.objects.exists())
