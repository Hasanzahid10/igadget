import io
import base64
import uuid
from PIL import Image
from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import Banner, PromoSection


def process_base64_image(image_input, max_size=(1600, 1600), quality=80):
    if isinstance(image_input, str) and image_input.startswith('data:image/'):
        try:
            format_str, imgstr = image_input.split(';base64,')
            img_bytes = base64.b64decode(imgstr)
            img = Image.open(io.BytesIO(img_bytes))
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                mask = img.split()[-1] if 'A' in img.mode else None
                background.paste(img, mask=mask)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            buffer.seek(0)
            filename = f"{uuid.uuid4().hex}.jpg"
            return ContentFile(buffer.read(), name=filename)
        except Exception:
            try:
                format_str, imgstr = image_input.split(';base64,')
                filename = f"{uuid.uuid4().hex}.jpg"
                return ContentFile(base64.b64decode(imgstr), name=filename)
            except Exception:
                pass
    return None


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'

    def create(self, validated_data):
        img_data = validated_data.get('image_url')
        cfile = process_base64_image(img_data)
        if cfile:
            banner = Banner(**validated_data)
            banner.image_file.save(cfile.name, cfile, save=False)
            banner.image_url = banner.image_file.url if banner.image_file else img_data
            banner.save()
            return banner
        return super().create(validated_data)

    def update(self, instance, validated_data):
        img_data = validated_data.get('image_url')
        cfile = process_base64_image(img_data)
        if cfile:
            instance.image_file.save(cfile.name, cfile, save=False)
            validated_data['image_url'] = instance.image_file.url if instance.image_file else img_data
        return super().update(instance, validated_data)


class PromoSectionSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = PromoSection
        fields = ('id', 'title', 'subtitle', 'icon_url', 'action_link', 'type', 'type_display')