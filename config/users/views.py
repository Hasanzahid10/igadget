import datetime
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import OTPVerification, Address, UserActivity
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    OTPVerificationSerializer,
    ChangePasswordOTPVerificationSerializer,
    SentOtpPasswordVerificationSerializer,
    UserLoginSerializer,
    AddressSerializer,
    get_token,  # Imported the standalone token helper
)

User = get_user_model()


# ================================================
# User Viewset
# ================================================

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'register']:
            return UserRegistrationSerializer
        elif self.action == 'login':
            return UserLoginSerializer
        elif self.action == 'verify_otp':
            return OTPVerificationSerializer
        elif self.action == 'sentOtpForPasswordChange':
            return SentOtpPasswordVerificationSerializer
        elif self.action == 'ChangePasswordOtpVerification':
            return ChangePasswordOTPVerificationSerializer
        return UserProfileSerializer

    def get_permissions(self):
        if self.action in ['create', 'register', 'login', 'verify_otp','sentOtpForPasswordChange',
        'ChangePasswordOtpVerification', 'track_activity', 'activities']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        return self.register(request)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_token(user)
            return Response({
                "message": "User registered successfully.",
                "access": tokens['access'],
                "refresh": tokens['refresh'],
                "access_token_type": tokens['access_token_type'],
                "user": UserProfileSerializer(user, context={"request": request}).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ===================================================
    # Track User / Guest Activity
    # ===================================================
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def track_activity(self, request):
        action_type = request.data.get('action')
        if not action_type:
            return Response({"error": "action is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if request.user.is_authenticated else None
        user_type = 'registered' if user else 'guest'
        session_id = request.data.get('session_id', '')
        
        user_identifier = request.data.get('user_identifier', '')
        if not user_identifier:
            if user:
                user_identifier = user.name or user.email
            else:
                user_identifier = f"Guest-{session_id[:6]}" if session_id else "Guest Visitor"

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        from .models import UserActivity
        from .serializers import UserActivitySerializer

        activity = UserActivity.objects.create(
            user=user,
            session_id=session_id,
            user_type=user_type,
            user_identifier=user_identifier,
            action=action_type,
            product_id=request.data.get('product_id'),
            product_title=request.data.get('product_title', ''),
            product_image=request.data.get('product_image', ''),
            product_price=request.data.get('product_price'),
            metadata=request.data.get('metadata', {}),
            ip_address=ip_address
        )
        serializer = UserActivitySerializer(activity)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ===================================================
    # Get Activities & Visitor Stats (For Admin Live Radar)
    # ===================================================
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def activities(self, request):
        from .models import UserActivity
        from .serializers import UserActivitySerializer
        import datetime

        limit = int(request.query_params.get('limit', 100))
        activities_qs = UserActivity.objects.all().order_by('-created_at')[:limit]
        serializer = UserActivitySerializer(activities_qs, many=True)

        last_24h = timezone.now() - datetime.timedelta(hours=24)
        recent_qs = UserActivity.objects.filter(created_at__gte=last_24h)

        total_activities = UserActivity.objects.count()
        guest_count = recent_qs.filter(user_type='guest').values('session_id').distinct().count()
        registered_count = recent_qs.filter(user_type='registered').values('user').distinct().count()
        views_count = recent_qs.filter(action='view_product').count()
        cart_count = recent_qs.filter(action='add_to_cart').count()
        wishlist_count = recent_qs.filter(action='add_to_wishlist').count()

        return Response({
            "activities": serializer.data,
            "stats": {
                "total_activities": total_activities,
                "active_guests_24h": guest_count,
                "active_registered_24h": registered_count,
                "product_views_24h": views_count,
                "cart_adds_24h": cart_count,
                "wishlist_adds_24h": wishlist_count,
            }
        }, status=status.HTTP_200_OK)

    # ================================================
    # User verify OTP View
    # =================================================
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def verify_otp(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "OTP verified successfully. You can login now."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ===================================================
    # User Login
    # ===================================================
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            # Get the validated User model instance (not a dictionary)
            user = serializer.validated_data['user']
            tokens = get_token(user)

            return Response({
                'message': 'Your login was successful',
                'access': tokens['access'],
                'refresh': tokens['refresh'],
                'access_token_type': tokens['access_token_type'],
                'user': UserProfileSerializer(user, context={"request": request}).data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ===================================================
    # Resent OTP
    # ===================================================
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def sentOtpForPasswordChange(self, request):
        serializer = SentOtpPasswordVerificationSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # =================================================
    # Change Password OTP Verification
    # ==================================================
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def ChangePasswordOtpVerification(self, request):
        serializer = ChangePasswordOTPVerificationSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ================================================
    # User Profile View (/api/users/me/)
    # =================================================
    @action(detail=False, methods=['get', 'put', 'patch', 'delete'])
    def me(self, request):
        """
        Custom action to manage the currently logged-in user's profile.
        Routes to: /api/users/me/
        """
        user = request.user

        if request.method == 'GET':
            serializer = UserProfileSerializer(user, context={'request': request})
            return Response(serializer.data)

        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = UserProfileSerializer(user, data=request.data, partial=partial, context={'request': request})
            serializer.is_valid(raise_exception=True)
            updated_user = serializer.save()
            response_serializer = UserProfileSerializer(updated_user, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            user.delete()
            return Response(
                {"detail": "User account deleted successfully."},
                status=status.HTTP_204_NO_CONTENT
            )

    # ================================================
    # Address Management Viewset (/api/users/address/)
    # ================================================
    @action(detail=False, methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
            permission_classes=[permissions.IsAuthenticated])
    def address(self, request):
        user = request.user

        if request.method == "GET":
            addresses = Address.objects.filter(user=user).order_by('-is_default', '-id')
            serializer = AddressSerializer(addresses, many=True, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == "POST":
            current_count = Address.objects.filter(user=user).count()
            if current_count >= 3:
                return Response(
                    {"error": "Maximum limit of 3 saved addresses reached. Please edit or remove an existing address."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = AddressSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                is_default = request.data.get('is_default', current_count == 0)
                if is_default:
                    Address.objects.filter(user=user).update(is_default=False)
                addr = serializer.save(user=user, is_default=is_default)
                
                # If user phone was empty, sync from address phone
                if not user.phone and request.data.get('phone'):
                    user.phone = request.data.get('phone')
                    user.save(update_fields=['phone'])

                return Response(AddressSerializer(addr).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if request.method in ["PUT", "PATCH"]:
            address_id = request.data.get("id") or request.query_params.get("id")
            if not address_id:
                return Response({"error": "Address ID is required for update."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                address_obj = Address.objects.get(id=address_id, user=user)
            except Address.DoesNotExist:
                return Response({"error": "Address not found."}, status=status.HTTP_404_NOT_FOUND)

            is_default = request.data.get('is_default')
            if is_default in [True, "True", "true", 1]:
                Address.objects.filter(user=user).exclude(id=address_obj.id).update(is_default=False)

            partial = request.method == "PATCH"
            serializer = AddressSerializer(address_obj, data=request.data, partial=partial, context={"request": request})
            if serializer.is_valid():
                updated_addr = serializer.save()
                if is_default in [True, "True", "true", 1]:
                    updated_addr.is_default = True
                    updated_addr.save(update_fields=['is_default'])
                return Response(AddressSerializer(updated_addr).data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if request.method == "DELETE":
            address_id = request.data.get("id") or request.query_params.get("id")
            if not address_id:
                return Response({"error": "Address ID is required for deletion."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                address_obj = Address.objects.get(id=address_id, user=user)
                was_default = address_obj.is_default
                address_obj.delete()

                # If default address was deleted, promote another address to default
                if was_default:
                    first_rem = Address.objects.filter(user=user).first()
                    if first_rem:
                        first_rem.is_default = True
                        first_rem.save(update_fields=['is_default'])

                return Response({"message": "Address deleted successfully."}, status=status.HTTP_200_OK)
            except Address.DoesNotExist:
                return Response({"error": "Address not found."}, status=status.HTTP_404_NOT_FOUND)