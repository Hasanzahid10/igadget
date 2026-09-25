import uuid
from django.db import models
from django.utils.text import slugify

#==================================================
# Category Model
#===================================================

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name 


#================================================
# Brand Model
#================================================
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    logo = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


#======================================================================
# Product Model
#======================================================================

class Products(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_deal_of_the_day = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, null=True, related_name='products')
    badge = models.CharField(max_length=100, blank=True, null=True)
    storage_options = models.JSONField(default=list, blank=True)
    colors = models.JSONField(default=list, blank=True)
    specs = models.JSONField(default=list, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'product'
            slug = base_slug
            counter = 1
            while Products.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        # Calculate discount percentage 
        if self.price and self.discount_price and self.discount_price < self.price:
            discount = ((self.price - self.discount_price) / self.price) * 100
            self.discount_percentage = round(discount)
        else:
            self.discount_percentage = 0

        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title


#===============================================
# Products Image Model
#===============================================
class ProductsImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='images')
    images = models.TextField(null=True, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"image for {self.product.title}"
