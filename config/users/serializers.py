from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OTPVerification, Address, UserActivity

User = get_user_model()

# =======================================================
# Standalone Token Generator Helper Function
# =======================================================
def get_token(user):
    """
    Generates JWT tokens for a given User instance.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'access_token_type': 'Bearer',
    }

# ================================================
# User Registration Serializer
# ================================================
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'phone', 'role', 'password', 'created_at')
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            phone=validated_data.get('phone', ''),
            role=validated_data.get('role', getattr(User.Role, 'CUSTOMER', 'customer')),
            is_active=True,  # Active for immediate authenticated checkout
        )
        return user


# =======================================================
# User Activity Serializer (Guest & Registered Tracking)
# =======================================================
class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = '__all__'



# =======================================================
# OTP Verification Serializer
# =======================================================
class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        email = attrs.get("email")
        code = attrs.get("code")

        if not email or not code:
            raise serializers.ValidationError({"error": "email and code are required"})

        # Fetch user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "User not found"})

        # OTP verification
        otp = OTPVerification.objects.filter(
            user=user,
            code=code,
            purpose="register",
            is_used=False,
        ).first()

        if not otp or not otp.is_valid():
            raise serializers.ValidationError({"error": "Invalid otp or expired"})

        otp.is_used = True
        otp.save()

        # Activate user account
        user.is_active = True
        user.save()

        return attrs


# ===========================================================
# Send OTP for Password Change Serializer
# ===========================================================
class SentOtpPasswordVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        email = attrs.get('email')

        if not email:
            raise serializers.ValidationError({"error": "email address is required."})
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "User not found."})

        # Sending OTP for password reset
        otp = OTPVerification.generate_otp(user, "reset")
        print(f"[DEBUG OTP] Password reset for {user.email}:{otp.code}")
        return attrs


# ===========================================================
# Change Password OTP Verification Serializer
# ===========================================================
class ChangePasswordOTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        attrs = super().validate(attrs)

        email = attrs.get('email')
        otp_code = attrs.get('otp')
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        if not all((email, otp_code, new_password, confirm_password)):
            raise serializers.ValidationError({"error": "These fields are required."})

        if new_password != confirm_password or len(new_password) < 6:
            raise serializers.ValidationError({"error": "confirm password does not match with new password"})

        # User lookup
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "User not found"})

        # OTP lookup & validation
        otp = OTPVerification.objects.filter(
            user=user,
            code=otp_code,
            purpose="reset",
            is_used=False,
        ).first()

        if not otp or not otp.is_valid():
            raise serializers.ValidationError({"error": "Invalid otp or expired"})

        # Mark OTP as used
        otp.is_used = True
        otp.save()

        # Update user password
        user.set_password(new_password)
        user.save()

        return attrs


# ===========================================================
# User Login Serializer
# ===========================================================
class UserLoginSerializer(serializers.Serializer):
    """Serializer used for user authentication & token generation"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError({"error": "These fields are required."})

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "Invalid Credentials."})

        if not user_obj.check_password(password):
            raise serializers.ValidationError({"error": "Invalid Credentials."})

        if not user_obj.is_active:
            raise serializers.ValidationError({"error": "User inactive. Please contact admin."})

        # Generate tokens passing the User model instance
        tokens = get_token(user_obj)

        return {
            'message': 'your login successfully',
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'access_token_type': tokens['access_token_type'],
            'user': user_obj
        }

    def to_representation(self, instance):
        user = instance.get('user') if isinstance(instance, dict) else getattr(instance, 'user', None)
        if not user:
            return {}

        token_data = get_token(user)

        return {
            'message': instance.get('message', 'Your login successfully') if isinstance(instance, dict) else "Your login successfully",
            'access': token_data['access'],
            'refresh': token_data['refresh'],
            'access_token_type': token_data['access_token_type'],
            'user': {
                'id': user.id,
                'email': user.email,
                'name': getattr(user, 'name', ''),
            }
        }


# =====================================================================
# Address Serializer
# =====================================================================
class AddressSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Address
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'id': {'read_only': True},
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)

        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            attrs['user'] = user

            if attrs.get('is_default'):
                default_address = Address.objects.filter(user=user, is_default=True).first()
                if default_address:
                    default_address.is_default = False
                    default_address.save()

        return attrs


# =======================================================
# User Profile Serializer
# =======================================================
class UserProfileSerializer(serializers.ModelSerializer):
    address = AddressSerializer(source="user_addresses", many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'phone', 'role', 'created_at', 'address')
        read_only_fields = ('id', 'email', 'role', 'created_at', 'address')

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        if address_data is None:
            address_data = validated_data.pop('user_addresses', None)

        instance.name = validated_data.get('name', instance.name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.save()

        if address_data is not None:
            for item in address_data:
                address_id = item.get('id')
                if address_id:
                    Address.objects.filter(id=address_id, user=instance).update(
                        address_line1=item.get('address_line1'),
                        address_line2=item.get('address_line2'),
                        city=item.get('city'),
                        state=item.get('state'),
                        phone=item.get('phone')
                    )
        return instance

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if response.get('address'):
            address_data = response['address']
            default_address = next((item for item in address_data if item.get('is_default') in [True, "True"]), None)
            response['default_address'] = default_address
        return response