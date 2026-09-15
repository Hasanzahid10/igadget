from rest_framework import serializers
from .models import Banner, PromoSection

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'


class PromoSectionSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = PromoSection
        fields = ('id', 'title', 'subtitle', 'icon_url', 'action_link', 'type', 'type_display')