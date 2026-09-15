import pytest
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from users.models import OTPVerification, Address

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_test_user():
    def _create_user(email="testpytest@example.com", name="Pytest User", password="password123", is_active=True, role=User.Role.CUSTOMER):
        return User.objects.create_user(
            email=email,
            name=name,
            password=password,
            is_active=is_active,
            role=role
        )
    return _create_user


@pytest.mark.django_db
class TestUserModelPytest:
    """Pytest test suite for User model."""

    def test_create_user(self):
        user = User.objects.create_user(
            email="user_pytest@example.com",
            name="Pytest User",
            password="securepassword"
        )
        assert user.email == "user_pytest@example.com"
        assert user.check_password("securepassword") is True
        assert user.role == User.Role.CUSTOMER
        assert str(user) == f"user_pytest@example.com ({User.Role.CUSTOMER})"

    def test_create_user_missing_email_raises_error(self):
        with pytest.raises(ValueError, match="Users must have an email address."):
            User.objects.create_user(email="", name="No Email", password="password123")

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin_pytest@example.com",
            name="Admin Pytest",
            password="adminpassword"
        )
        assert admin.role == User.Role.ADMIN
        assert admin.is_staff is True
        assert admin.is_superuser is True


@pytest.mark.django_db
class TestOTPVerificationPytest:
    """Pytest test suite for OTP verification logic."""

    def test_generate_and_validate_otp(self, create_test_user):
        user = create_test_user()
        otp = OTPVerification.generate_otp(user, purpose="register")
        assert otp.user == user
        assert len(otp.code) == 6
        assert otp.is_valid() is True

    def test_expired_otp(self, create_test_user):
        user = create_test_user()
        otp = OTPVerification.generate_otp(user, purpose="register")
        otp.created_at = timezone.now() - timedelta(minutes=15)
        otp.save()
        assert otp.is_valid() is False


@pytest.mark.django_db
class TestUserAPIPytest:
    """Pytest test suite for DRF user endpoints."""

    def test_register_and_verify_user(self, api_client):
        payload = {
            "name": "Pytest EndUser",
            "email": "enduser@example.com",
            "password": "password123",
            "phone": "01711112222"
        }
        # 1. Register
        res = api_client.post("/api/users/register/", payload)
        assert res.status_code == status.HTTP_201_CREATED
        assert "otp" in res.data

        otp_code = res.data["otp"]
        user = User.objects.get(email="enduser@example.com")
        assert user.is_active is False

        # 2. Verify OTP
        verify_payload = {"email": "enduser@example.com", "code": otp_code}
        res_verify = api_client.post("/api/users/verify_otp/", verify_payload)
        assert res_verify.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.is_active is True

    def test_login_success(self, api_client, create_test_user):
        create_test_user(email="logintest@example.com", password="password123", is_active=True)
        login_payload = {"email": "logintest@example.com", "password": "password123"}

        res = api_client.post("/api/users/login/", login_payload)
        assert res.status_code == status.HTTP_200_OK
        assert "access_token" in res.data
        assert "refresh_token" in res.data

    def test_authenticated_me_endpoint(self, api_client, create_test_user):
        user = create_test_user(email="me_pytest@example.com", is_active=True)
        api_client.force_authenticate(user=user)

        res = api_client.get("/api/users/me/")
        assert res.status_code == status.HTTP_200_OK
        assert res.data["email"] == "me_pytest@example.com"
