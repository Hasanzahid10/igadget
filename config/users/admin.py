from django.contrib import admin
from .models import User, Address, OTPVerification

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'phone', 'role', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'role']
    search_fields = ['email', 'name', 'phone']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'address_line1', 'address_line2', 'city', 'state', 'phone', 'is_default']
    list_filter = ['is_default', 'city', 'state']
    search_fields = ['user__email', 'address_line1', 'address_line2', 'city', 'state', 'phone']

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'purpose', 'created_at', 'is_used']
    list_filter = ['purpose', 'is_used']
    search_fields = ['user__email', 'code']
    ordering = ['-created_at']
    list_per_page = 20
