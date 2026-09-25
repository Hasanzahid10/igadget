import random
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

#================================================
# User Manager Model 
#================================================
class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address.')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)  # Hashes password automatically
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('role', User.Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, name, password, **extra_fields)

#=====================================================
# User Model 
#===================================================== 

class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        ADMIN = 'admin', 'Admin'

    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.CUSTOMER
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"{self.email} ({self.role})"

#================================================
# otp models
#================================================
class OTPVerification(models.Model):
    PURPOSE_CHOICES = (
        ('register', 'Registration'),
        ('reset', 'Password Reset'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        # OTP valid for 10 minutes
        return not self.is_used and (timezone.now() - self.created_at).total_seconds() < 600

    @classmethod
    def generate_otp(cls, user, purpose):
        code = str(random.randint(100000, 999999))
        return cls.objects.create(user=user, code=code, purpose=purpose)
    

#=============================================================
#  Address 
#=============================================================

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name = 'user_addresses')
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255,null=True,blank=True)
    city= models.CharField(max_length=255)
    state = models.CharField(max_length=255, null= True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    is_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user).update(is_default=False)
        super(Address,self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.state}"


#=============================================================
#  User Activity Tracking (Guest & Registered Visitor Radar)
#=============================================================
class UserActivity(models.Model):
    ACTION_CHOICES = (
        ('view_product', 'Viewed Product'),
        ('add_to_cart', 'Added to Cart'),
        ('remove_from_cart', 'Removed from Cart'),
        ('add_to_wishlist', 'Saved to Wishlist'),
        ('remove_from_wishlist', 'Removed from Wishlist'),
        ('checkout_start', 'Initiated Checkout'),
        ('order_placed', 'Placed Order'),
        ('search', 'Searched Products'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    session_id = models.CharField(max_length=255, blank=True, default='')
    user_type = models.CharField(max_length=20, default='guest')  # 'guest' or 'registered'
    user_identifier = models.CharField(max_length=255, default='Guest Visitor')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    product_id = models.CharField(max_length=255, null=True, blank=True)
    product_title = models.CharField(max_length=255, blank=True, default='')
    product_image = models.TextField(blank=True, default='')
    product_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_identifier} - {self.action} - {self.product_title}"
