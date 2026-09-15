from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from catalog.models import Category, Brand, Products
from .models import Cart, CartItem

User = get_user_model()


class CartModelTestCase(TestCase):
    """Test suite for Cart and CartItem model logic."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="cartuser@example.com",
            name="Cart User",
            password="password123"
        )
        self.category = Category.objects.create(name="Electronics")
        self.brand = Brand.objects.create(name="TechBrand")

        self.product1 = Products.objects.create(
            title="Laptop",
            description="High performance laptop",
            price=1000.00,
            discount_price=900.00,
            stock=10,
            category=self.category,
            brand=self.brand
        )
        self.product2 = Products.objects.create(
            title="Mouse",
            description="Wireless mouse",
            price=50.00,
            stock=20,
            category=self.category,
            brand=self.brand
        )

    def test_anonymous_cart_generates_session_token(self):
        cart = Cart.objects.create()
        self.assertIsNotNone(cart.session_token)
        self.assertIn("Cart", str(cart))

    def test_cart_total_price_and_items(self):
        cart = Cart.objects.create(user=self.user)
        item1 = CartItem.objects.create(cart=cart, product=self.product1, quantity=2)
        item2 = CartItem.objects.create(cart=cart, product=self.product2, quantity=1)

        # product1 effective price is discount_price = 900.00 -> 2 * 900 = 1800
        # product2 price = 50.00 -> 1 * 50 = 50
        # Total = 1850.00
        self.assertEqual(item1.subtotal, 1800.00)
        self.assertEqual(item2.subtotal, 50.00)
        self.assertEqual(cart.total_items, 3)
        self.assertEqual(cart.total_price, 1850.00)


class CartAPITestCase(APITestCase):
    """Test suite for Cart API endpoints."""

    def setUp(self):
        self.cart_url = "/api/cart/cart/"
        self.add_item_url = "/api/cart/cart/add_item/"
        self.update_item_url = "/api/cart/cart/update_item/"
        self.remove_item_url = "/api/cart/cart/remove_item/"
        self.clear_cart_url = "/api/cart/cart/clear/"

        self.user = User.objects.create_user(
            email="cartapi@example.com",
            name="Cart API User",
            password="password123",
            is_active=True
        )
        self.category = Category.objects.create(name="Gadgets")
        self.brand = Brand.objects.create(name="GadgetBrand")

        self.product = Products.objects.create(
            title="Smartphone",
            description="Flagship smartphone",
            price=800.00,
            stock=5,
            category=self.category,
            brand=self.brand
        )

    def test_get_cart_authenticated(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.cart_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["user"], self.user.id)

    def test_get_cart_anonymous_with_session_token(self):
        headers = {"HTTP_X_SESSION_TOKEN": "custom-session-12345"}
        res = self.client.get(self.cart_url, **headers)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["session_token"], "custom-session-12345")

    def test_add_item_to_cart_success(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "product_id": self.product.id,
            "quantity": 2
        }
        res = self.client.post(self.add_item_url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["total_items"], 2)
        self.assertEqual(float(res.data["total_price"]), 1600.00)

    def test_add_item_insufficient_stock(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "product_id": self.product.id,
            "quantity": 10  # Only 5 in stock
        }
        res = self.client.post(self.add_item_url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", res.data)

    def test_update_item_quantity(self):
        self.client.force_authenticate(user=self.user)
        # First add item
        self.client.post(self.add_item_url, {"product_id": self.product.id, "quantity": 1})
        
        cart = Cart.objects.get(user=self.user)
        item = cart.items.first()

        update_payload = {
            "item_id": item.id,
            "quantity": 3
        }
        res = self.client.patch(self.update_item_url, update_payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["total_items"], 3)

    def test_update_item_zero_quantity_removes_item(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self.add_item_url, {"product_id": self.product.id, "quantity": 1})
        
        cart = Cart.objects.get(user=self.user)
        item = cart.items.first()

        update_payload = {
            "item_id": item.id,
            "quantity": 0
        }
        res = self.client.patch(self.update_item_url, update_payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["total_items"], 0)

    def test_remove_item(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self.add_item_url, {"product_id": self.product.id, "quantity": 1})
        
        cart = Cart.objects.get(user=self.user)
        item = cart.items.first()

        res = self.client.delete(self.remove_item_url, {"item_id": item.id}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["total_items"], 0)

    def test_clear_cart(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self.add_item_url, {"product_id": self.product.id, "quantity": 2})

        res = self.client.delete(self.clear_cart_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["total_items"], 0)
        self.assertEqual(len(res.data["items"]), 0)
