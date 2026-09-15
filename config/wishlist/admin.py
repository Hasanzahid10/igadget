from django.contrib import admin
from .models import Wishlist

#==============================================
# and addmin in site
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    # Display key details in the list table
    list_display = ('id', 'get_user_email', 'get_product_title', 'added_at')

    # Filter records by date added
    list_filter = ('added_at',)

    # Enable search by user email, user name, and product title
    search_fields = ('user__email', 'user__name', 'product__title')

    # Read-only fields to prevent manual editing of auto-generated fields
    readonly_fields = ('added_at',)

    # Optimize query performance for ForeignKeys
    raw_id_fields = ('user', 'product')
    ordering = ('-added_at',)

#===================================================
#
#===================================================

    # Custom methods for cleaner admin column titles
    @admin.display(description='User Email', ordering='user__email')
    def get_user_email(self, obj):
        return obj.user.email

    @admin.display(description='Product Title', ordering='product__title')
    def get_product_title(self, obj):
        return obj.product.title