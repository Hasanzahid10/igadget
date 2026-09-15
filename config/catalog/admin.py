from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Products, ProductsImage


class ProductsImageInline(admin.TabularInline):
    model = ProductsImage
    extra = 1
    fields = ('images', 'is_primary', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.images:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />', obj.images)
        return "No Image"
    image_preview.short_description = "Preview"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'icon', 'is_active')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('parent',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'logo_preview')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: contain;" />', obj.logo)
        return "-"
    logo_preview.short_description = "Logo"


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'brand',
        'price',
        'discount_price',
        'discount_percentage',
        'stock',
        'is_featured',
        'is_deal_of_the_day',
        'is_active',
        'create_at',
    )
    list_filter = ('is_active', 'is_featured', 'is_deal_of_the_day', 'category', 'brand')
    search_fields = ('title', 'description', 'category__name', 'brand__name')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('category', 'brand')
    readonly_fields = ('discount_percentage', 'create_at', 'update_at')
    inlines = [ProductsImageInline]

    actions = ['mark_as_featured', 'unmark_featured', 'mark_as_deal', 'unmark_deal', 'activate_products', 'deactivate_products']

    fieldsets = (
        ('Basic Details', {
            'fields': ('title', 'slug', 'description', 'category', 'brand', 'is_active')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'discount_price', 'discount_percentage', 'stock')
        }),
        ('Promotions & Badges', {
            'fields': ('is_featured', 'is_deal_of_the_day')
        }),
        ('Timestamps', {
            'fields': ('create_at', 'update_at')
        }),
    )

    # Bulk Actions
    @admin.action(description='⭐ Mark selected products as Featured')
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description='Unmark selected products as Featured')
    def unmark_featured(self, request, queryset):
        queryset.update(is_featured=False)

    @admin.action(description='🔥 Mark selected products as Deal of the Day')
    def mark_as_deal(self, request, queryset):
        queryset.update(is_deal_of_the_day=True)

    @admin.action(description='Unmark selected products as Deal of the Day')
    def unmark_deal(self, request, queryset):
        queryset.update(is_deal_of_the_day=False)

    @admin.action(description='✅ Activate selected products')
    def activate_products(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='🚫 Deactivate selected products')
    def deactivate_products(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(ProductsImage)
class ProductsImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_primary', 'image_preview')
    list_filter = ('is_primary',)
    raw_id_fields = ('product',)

    def image_preview(self, obj):
        if obj.images:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />', obj.images)
        return "No Image"
    image_preview.short_description = "Preview"