from django.contrib import admin, messages
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'unit_price', 'quantity', 'get_subtotal')
    can_delete = False
    fields = ('product', 'unit_price', 'quantity', 'get_subtotal')

    @admin.display(description='Subtotal')
    def get_subtotal(self, obj):
        if obj and obj.subtotal is not None:
            return f"${obj.subtotal:.2f}"
        return f"${obj.subtotal:.2f}" if obj.subtotal else "$0.00"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Display key columns in the main admin table
    list_display = (
        'order_number',
        'get_customer_name',
        'clickable_phone',
        'total_amount',
        'status',
        'payment_status',
        'created_at',
    )

    # Sidebar filtering
    list_filter = ('status', 'payment_status', 'created_at')

    # Quick search across order numbers, phone numbers, and user emails
    search_fields = ('order_number', 'phone_number', 'user__email', 'user__name')

    # Read-only fields to prevent accidental edits
    readonly_fields = ('order_number', 'total_amount', 'created_at')

    # Render order items inline inside the order detail page
    inlines = [OrderItemInline]

    # Bulk actions for order status workflows
    actions = ['confirm_order_by_call', 'mark_as_shipped', 'mark_as_delivered', 'cancel_order']

    # Fieldsets for structured detail view layout
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'phone_number', 'created_at')
        }),
        ('Status & Payment', {
            'fields': ('status', 'payment_status', 'total_amount', 'shipping_fee')
        }),
        ('Shipping Details', {
            'fields': ('shipping_address',)
        }),
    )

    @admin.display(description='Customer', ordering='user__email')
    def get_customer_name(self, obj):
        if hasattr(obj.user, 'name') and obj.user.name:
            return f"{obj.user.name} ({obj.user.email})"
        return obj.user.email

    @admin.display(description='Phone (Click to Call)', ordering='phone_number')
    def clickable_phone(self, obj):
        if obj.phone_number:
            return format_html(
                '<a href="tel:{}" style="font-weight: bold; color: #2b6cb0;">📞 {}</a>',
                obj.phone_number,
                obj.phone_number
            )
        return "No Phone"

    # ====================================================
    # Custom Bulk Actions
    # ====================================================

    @admin.action(description='✅ Confirm selected orders (Phone Verified)')
    def confirm_order_by_call(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='processing')
        self.message_user(
            request,
            f"Successfully confirmed {updated} order(s) and set status to Processing.",
            messages.SUCCESS
        )

    @admin.action(description='🚚 Mark selected orders as Shipped')
    def mark_as_shipped(self, request, queryset):
        updated = queryset.filter(status='processing').update(status='shipped')
        self.message_user(
            request,
            f"Successfully marked {updated} order(s) as Shipped.",
            messages.SUCCESS
        )

    @admin.action(description='📦 Mark selected orders as Delivered')
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(
            request,
            f"Successfully marked {updated} order(s) as Delivered.",
            messages.SUCCESS
        )

    @admin.action(description='❌ Cancel selected orders')
    def cancel_order(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(
            request,
            f"Successfully cancelled {updated} order(s).",
            messages.WARNING
        )

