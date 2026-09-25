from rest_framework import serializers
from .models import Products, Brand, Category, ProductsImage

#================================================
# Category Serializer
#================================================
class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'
        extra_kwargs = {
            "slug": {"read_only": True},
            "parent": {"required": False},
        }
    
    def get_subcategories(self, obj):
        subcategories = obj.subcategories.filter(is_active=True)
        return CategorySerializer(subcategories, many=True).data

    def get_products_count(self, obj):
        return obj.products.filter(is_active=True).count() if hasattr(obj, 'products') else 0


#================================================
# Brand Serializer
#================================================
class BrandSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    active_products_count = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = '__all__'
        extra_kwargs = {
            "slug": {"read_only": True},
            "logo": {"required": False}
        }
    
    def get_products_count(self, obj):
        return obj.products.count()

    def get_active_products_count(self, obj):
        return obj.products.filter(is_active=True).count()


#=================================================
# Product Image Serializer
#=================================================
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsImage
        fields = '__all__'


#=================================================
# Product List Serializer
#=================================================
class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Products
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True},
            'discount_price': {'required': False},
            'discount_percentage': {'read_only': True},
            'stock': {'required': False},
            'category': {'required': False},
            'brand': {'required': False},
            'create_at': {'read_only': True},
            'update_at': {'read_only': True}
        }

    def get_primary_image(self, obj):
        primary_img = obj.images.filter(is_primary=True).first()
        return primary_img.images if primary_img else None


#=====================================================
# Product Detail Serializer
#=====================================================
class ProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Products
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True},
            'discount_price': {'required': False},
            'discount_percentage': {'read_only': True},
            'stock': {'required': False},
            'category': {'required': False},
            'brand': {'required': False},
            'create_at': {'read_only': True},
            'update_at': {'read_only': True}
        }