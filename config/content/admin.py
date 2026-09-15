from django.contrib import admin
from .models import Banner, PromoSection

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'badge_text', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    search_fields = ('title', 'subtitle', 'primary_button_text', 'secondary_button_text')


@admin.register(PromoSection)
class PromoSectionAdmin(admin.ModelAdmin):
    list_display = ('get_type_display', 'title', 'action_link')
    list_filter = ('type',)
    search_fields = ('title', 'subtitle', 'action_link')
    ordering = ('type',)
