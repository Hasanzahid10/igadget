from django.db import models
from django.contrib.auth import get_user_model
from catalog.models import Products  # Adjust import based on your app name
# get user
User = get_user_model()

#====================================================
# create a wishlist
#====================================================

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='in_wishlists')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.email} - {self.product.title}"

