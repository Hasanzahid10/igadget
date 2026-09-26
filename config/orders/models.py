import uuid
from django.db import models
from django.contrib.auth import get_user_model
from catalog.models import Products

User = get_user_model()


class DeliverySetting(models.Model):
    inside_dhaka_fee = models.DecimalField(max_digits=10, decimal_places=2, default=70.00, help_text="Delivery fee inside Dhaka (BDT)")
    outside_dhaka_fee = models.DecimalField(max_digits=10, decimal_places=2, default=130.00, help_text="Delivery fee outside Dhaka (BDT)")
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00, help_text="Order amount threshold for free shipping (0 to disable)")
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Delivery Setting"
        verbose_name_plural = "Delivery Settings"

    @classmethod
    def get_settings(cls):
        setting, _ = cls.objects.get_or_create(id=1, defaults={
            'inside_dhaka_fee': 70.00,
            'outside_dhaka_fee': 130.00,
            'free_shipping_threshold': 5000.00
        })
        return setting

    def __str__(self):
        return f"Inside Dhaka: ৳{self.inside_dhaka_fee} | Outside Dhaka: ৳{self.outside_dhaka_fee}"


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )

    DELIVERY_ZONE_CHOICES = (
        ('inside_dhaka', 'Inside Dhaka'),
        ('outside_dhaka', 'Outside Dhaka'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    order_number = models.CharField(max_length=100, unique=True, blank=True)
    tracking_token = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    
    # Guest / Customer Details
    customer_name = models.CharField(max_length=150, blank=True, default='', help_text="Customer name")
    customer_email = models.EmailField(blank=True, default='', help_text="Customer email")
    customer_phone = models.CharField(max_length=50, default='', blank=True, help_text="Phone number for order confirmation calls")
    
    # Pricing & Delivery
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=70.00)
    delivery_zone = models.CharField(max_length=50, choices=DELIVERY_ZONE_CHOICES, default='inside_dhaka')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    shipping_address = models.JSONField(default=dict)  # Stores full snapshot of address at time of order
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_guest(self):
        return self.user is None

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        if not self.tracking_token:
            self.tracking_token = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        customer = self.customer_name or (self.user.email if self.user else self.customer_phone) or "Guest"
        return f"Order {self.order_number} - {customer}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Products, on_delete=models.PROTECT)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        if self.unit_price is None or self.quantity is None:
            return 0
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.title} (Order: {self.order.order_number})"