from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import OTPVerification, Address

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
        'ChangePasswordOtpVerification']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        return self.register(request)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Retrieve the automatically generated registration OTP
            otp = OTPVerification.objects.filter(user=user, purpose='register', is_used=False).first()
            otp_code = otp.code if otp else None
            return Response({
                "message": "User registered successfully. Please verify your email ID.",
                "otp": otp_code  # Returned in response for testing convenience
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        if request.method == "POST":
            serializer = AddressSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response({"message": "Address added successfully"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if request.method in ["PUT", "PATCH"]:
            address_id = request.data.get("id")
            if address_id:
                try:
                    address = Address.objects.get(id=address_id, user=request.user)
                except Address.DoesNotExist:
                    return Response({"error": "Address not found"}, status=status.HTTP_404_NOT_FOUND)

                partial = request.method == "PATCH"
                serializer = AddressSerializer(address, data=request.data, partial=partial,
                                               context={"request": request})
                if serializer.is_valid():
                    serializer.save()
                    return Response({"message": "Address updated successfully"}, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Address ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == "GET":
            addresses = Address.objects.filter(user=request.user)
            serializer = AddressSerializer(addresses, many=True, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == "DELETE":
            address_id = request.data.get("id")
            if not address_id:
                return Response({"error": "Address ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                address = Address.objects.get(id=address_id, user=request.user)
                address.delete()
                return Response({"message": "Address deleted successfully"}, status=status.HTTP_200_OK)
            except Address.DoesNotExist:
                return Response({"error": "Address not found"}, status=status.HTTP_404_NOT_FOUND)