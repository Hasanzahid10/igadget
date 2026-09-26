from django.contrib import admin, messages
from django.utils.html import format_html
from .models import Order, OrderItem, DeliverySetting


@admin.register(DeliverySetting)
class DeliverySettingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'inside_dhaka_fee', 'outside_dhaka_fee', 'free_shipping_threshold', 'updated_at')
    fields = ('inside_dhaka_fee', 'outside_dhaka_fee', 'free_shipping_threshold')

    def has_add_permission(self, request):
        # Prevent creating multiple instances if 1 already exists
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'unit_price', 'quantity', 'get_subtotal')
    can_delete = False
    fields = ('product', 'unit_price', 'quantity', 'get_subtotal')

    @admin.display(description='Subtotal')
    def get_subtotal(self, obj):
        if obj and obj.subtotal is not None:
            return f"৳{obj.subtotal:,.2f}"
        return "৳0.00"


class BuyerTypeFilter(admin.SimpleListFilter):
    title = 'Buyer Type'
    parameter_name = 'buyer_type'

    def lookups(self, request, model_admin):
        return (
            ('guest', '🚪 Guest Orders'),
            ('registered', '👤 Registered Users'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'guest':
            return queryset.filter(user__isnull=True)
        if self.value() == 'registered':
            return queryset.filter(user__isnull=False)
        return queryset


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'get_buyer_badge',
        'get_customer_info',
        'clickable_phone',
        'delivery_zone_display',
        'formatted_total',
        'status',
        'payment_status',
        'created_at',
    )

    list_filter = (BuyerTypeFilter, 'delivery_zone', 'status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'customer_name', 'customer_email', 'customer_phone', 'user__email', 'user__name', 'tracking_token')
    readonly_fields = ('order_number', 'tracking_token', 'total_amount', 'created_at')

    inlines = [OrderItemInline]
    actions = ['confirm_order_by_call', 'mark_as_shipped', 'mark_as_delivered', 'cancel_order']

    fieldsets = (
        ('Order Header', {
            'fields': ('order_number', 'tracking_token', 'user', 'created_at')
        }),
        ('Customer Info (Guest / Account)', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Status & Financials', {
            'fields': ('status', 'payment_status', 'delivery_zone', 'shipping_fee', 'total_amount')
        }),
        ('Shipping Address Details', {
            'fields': ('shipping_address',)
        }),
    )

    @admin.display(description='Buyer Type', ordering='user')
    def get_buyer_badge(self, obj):
        if obj.user:
            return format_html(
                '<span style="background-color: #e8f0fe; color: #1967d2; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">👤 Registered</span>'
            )
        return format_html(
            '<span style="background-color: #fef3c7; color: #92400e; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">🚪 Guest</span>'
        )

    @admin.display(description='Customer Info')
    def get_customer_info(self, obj):
        name = obj.customer_name or (obj.user.name if obj.user and hasattr(obj.user, 'name') else '') or "Guest"
        email = obj.customer_email or (obj.user.email if obj.user else '') or ""
        if email:
            return f"{name} ({email})"
        return name

    @admin.display(description='Phone', ordering='customer_phone')
    def clickable_phone(self, obj):
        phone = obj.customer_phone or (obj.user.phone if obj.user and hasattr(obj.user, 'phone') else '')
        if phone:
            return format_html(
                '<a href="tel:{}" style="font-weight: bold; color: #1a73e8;">📞 {}</a>',
                phone,
                phone
            )
        return "No Phone"

    @admin.display(description='Zone', ordering='delivery_zone')
    def delivery_zone_display(self, obj):
        if obj.delivery_zone == 'outside_dhaka':
            return format_html('<span style="color: #c5221f; font-weight: 600;">Outside Dhaka</span>')
        return format_html('<span style="color: #137333; font-weight: 600;">Inside Dhaka</span>')

    @admin.display(description='Total Amount', ordering='total_amount')
    def formatted_total(self, obj):
        return f"৳{obj.total_amount:,.2f}"

    # ====================================================
    # Custom Actions
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


