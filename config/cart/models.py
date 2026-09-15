import uuid
from django.db import models
from django.contrib.auth import get_user_model
from catalog.models import Products # Adjust import based on your app name

User = get_user_model()

#========================++++++++++++++++==================
# Create Cart item 
#========================++++++++++++++++==================
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    session_token = models.CharField(max_length=255, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Generate session_token if user is anonymous and no token exists
        if not self.user and not self.session_token:
            self.session_token = str(uuid.uuid4())
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f"Cart {self.id} - {'User: ' + self.user.email if self.user else 'Session: ' + str(self.session_token)}"

#-------------------------------------------------------------
# Create Cart item model
#-------------------------------------------------------------

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    @property
    def subtotal(self):
        effective_price = self.product.discount_price if self.product.discount_price else self.product.price
        return effective_price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"