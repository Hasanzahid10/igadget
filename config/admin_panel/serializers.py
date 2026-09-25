import uuid
from django.utils.text import slugify
from rest_framework import serializers
from catalog.models import Category, Products, ProductsImage, Brand
from orders.models import Order, OrderItem


class AdminProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsImage
        fields = '__all__'


class AdminProductSerializer(serializers.ModelSerializer):
    images = AdminProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model = Products
        fields = (
            'id', 'title', 'slug', 'description', 'price',
            'discount_price', 'discount_percentage', 'stock', 'category',
            'brand', 'is_featured', 'is_deal_of_the_day', 'images',
            'uploaded_images', 'category_name', 'brand_name',
            'storage_options', 'colors', 'specs', 'badge'
        )
        extra_kwargs = {
            'slug': {'read_only': True, 'required': False},
            'discount_percentage': {'read_only': True, 'required': False},
            'category': {'required': False, 'allow_null': True},
            'brand': {'required': False, 'allow_null': True},
            'description': {'required': False, 'allow_blank': True},
            'price': {'required': True},
            'stock': {'required': False},
            'storage_options': {'required': False},
            'colors': {'required': False},
            'specs': {'required': False},
            'badge': {'required': False, 'allow_blank': True, 'allow_null': True},
        }

    def _resolve_category(self, cat_input):
        if not cat_input:
            return None
        if isinstance(cat_input, Category):
            return cat_input
        # Support UUID lookup
        try:
            val = uuid.UUID(str(cat_input))
            cat = Category.objects.filter(id=val).first()
            if cat:
                return cat
        except (ValueError, AttributeError):
            pass
        if isinstance(cat_input, int) or (isinstance(cat_input, str) and str(cat_input).isdigit()):
            cat = Category.objects.filter(id=int(cat_input)).first()
            if cat:
                return cat
        cat_str = str(cat_input).strip()
        cat_aliases = {
            'phones': 'Smartphones',
            'mobile': 'Mobile',
            'laptops': 'Laptops',
            'computer': 'computer',
            'audio': 'Headphones & Audio',
            'headphone': 'Headphone',
            'watches': 'Smartwatches',
            'gaming': 'Gaming',
            'accessories': 'Accessories'
        }
        target_name = cat_aliases.get(cat_str.lower(), cat_str)
        cat = Category.objects.filter(slug__iexact=cat_str).first() or \
              Category.objects.filter(name__iexact=target_name).first() or \
              Category.objects.filter(name__iexact=cat_str).first()
        if not cat:
            cat = Category.objects.create(name=target_name, slug=slugify(cat_str) or 'general')
        return cat

    def _resolve_brand(self, brand_input):
        if not brand_input:
            return None
        if isinstance(brand_input, Brand):
            return brand_input
        if isinstance(brand_input, int) or (isinstance(brand_input, str) and str(brand_input).isdigit()):
            b = Brand.objects.filter(id=int(brand_input)).first()
            if b:
                return b
        brand_str = str(brand_input).strip()
        brand = Brand.objects.filter(name__iexact=brand_str).first()
        if not brand:
            brand = Brand.objects.create(name=brand_str, slug=slugify(brand_str) or 'brand')
        return brand

    def to_internal_value(self, data):
        mutable_data = data.copy() if hasattr(data, 'copy') else dict(data)

        # Support "name" as alias for "title"
        if 'name' in mutable_data and not mutable_data.get('title'):
            mutable_data['title'] = mutable_data['name']

        # Support "storageOptions" as alias for "storage_options"
        if 'storageOptions' in mutable_data and 'storage_options' not in mutable_data:
            mutable_data['storage_options'] = mutable_data['storageOptions']

        # Support "originalPrice" or "discountPrice" as discount_price
        if 'discountPrice' in mutable_data and not mutable_data.get('discount_price'):
            mutable_data['discount_price'] = mutable_data['discountPrice']
        elif 'originalPrice' in mutable_data and not mutable_data.get('discount_price'):
            mutable_data['discount_price'] = mutable_data['originalPrice']

        # Resolve category if string is passed
        raw_cat = mutable_data.get('category')
        if raw_cat is not None:
            cat_obj = self._resolve_category(raw_cat)
            if cat_obj:
                mutable_data['category'] = cat_obj.id

        # Resolve brand if string is passed
        raw_brand = mutable_data.get('brand')
        if raw_brand is not None:
            brand_obj = self._resolve_brand(raw_brand)
            if brand_obj:
                mutable_data['brand'] = brand_obj.id

        # Normalize images input (support images, gallery, uploaded_images, image)
        imgs = mutable_data.get('uploaded_images') or mutable_data.get('images') or mutable_data.get('gallery')
        if not imgs and mutable_data.get('image'):
            imgs = [mutable_data.get('image')]

        if imgs and isinstance(imgs, list):
            cleaned_imgs = []
            for item in imgs:
                if isinstance(item, dict) and 'url' in item:
                    cleaned_imgs.append(item['url'])
                elif isinstance(item, str) and item.strip():
                    cleaned_imgs.append(item.strip())
            mutable_data['uploaded_images'] = cleaned_imgs

        return super().to_internal_value(mutable_data)

    def create(self, validated_data):
        images_data = validated_data.pop('uploaded_images', [])
        product = super().create(validated_data)
        for idx, img_url in enumerate(images_data):
            if img_url:
                ProductsImage.objects.create(
                    product=product,
                    images=img_url,
                    is_primary=(idx == 0)
                )
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop('uploaded_images', None)
        product = super().update(instance, validated_data)
        if images_data is not None:
            if len(images_data) > 0:
                product.images.all().delete()
                for idx, img_url in enumerate(images_data):
                    if img_url:
                        ProductsImage.objects.create(
                            product=product,
                            images=img_url,
                            is_primary=(idx == 0)
                        )
        return product


class AdminCategorySerializer(serializers.ModelSerializer):
    icon_url = serializers.CharField(source='icon', allow_null=True, required=False)
    products_count = serializers.SerializerMethodField(read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = Category
        fields = (
            'id', 'name', 'slug', 'description', 'image',
            'icon_url', 'parent', 'parent_name', 'is_active', 'products_count'
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'slug': {'required': False},
            'description': {'required': False, 'allow_blank': True, 'allow_null': True},
            'image': {'required': False, 'allow_blank': True, 'allow_null': True},
            'parent': {'required': False, 'allow_null': True},
        }

    def get_products_count(self, obj):
        return obj.products.count() if hasattr(obj, 'products') else 0


class AdminOrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_title', 'unit_price', 'quantity', 'subtotal')


class AdminOrderSerializer(serializers.ModelSerializer):
    items = AdminOrderItemSerializer(many=True, read_only=True)
    customer_email = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'customer_email', 'phone_number',
            'total_amount', 'shipping_fee', 'status', 'payment_status',
            'shipping_address', 'created_at', 'items'
        )

    def get_customer_email(self, obj):
        if obj.user and getattr(obj.user, 'email', None):
            return obj.user.email
        if isinstance(obj.shipping_address, dict):
            return obj.shipping_address.get('email') or obj.shipping_address.get('name') or obj.shipping_address.get('fullName') or ''
        return ''