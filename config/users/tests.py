from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.test import TestCase
from users.models import OTPVerification, Address

User = get_user_model()


class UserModelTestCase(TestCase):
    """Test suite for User model and manager."""

    def test_create_user_successful(self):
        user = User.objects.create_user(
            email="testuser@example.com",
            name="Test User",
            password="password123",
            phone="1234567890"
        )
        self.assertEqual(user.email, "testuser@example.com")
        self.assertEqual(user.name, "Test User")
        self.assertTrue(user.check_password("password123"))
        self.assertEqual(user.role, User.Role.CUSTOMER)
        self.assertEqual(str(user), f"testuser@example.com ({User.Role.CUSTOMER})")

    def test_create_user_without_email_raises_value_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="",
                name="No Email User",
                password="password123"
            )

    def test_create_superuser_successful(self):
        admin = User.objects.create_superuser(
            email="admin@example.com",
            name="Admin User",
            password="adminpassword"
        )
        self.assertEqual(admin.role, User.Role.ADMIN)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class OTPVerificationModelTestCase(TestCase):
    """Test suite for OTPVerification model logic."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="otpuser@example.com",
            name="OTP User",
            password="password123"
        )

    def test_generate_otp(self):
        otp = OTPVerification.generate_otp(self.user, purpose="register")
        self.assertEqual(otp.user, self.user)
        self.assertEqual(len(otp.code), 6)
        self.assertEqual(otp.purpose, "register")
        self.assertFalse(otp.is_used)
        self.assertTrue(otp.is_valid())

    def test_otp_validity_expired(self):
        otp = OTPVerification.generate_otp(self.user, purpose="register")
        # Shift created_at time to 11 minutes ago
        otp.created_at = timezone.now() - timedelta(minutes=11)
        otp.save()
        self.assertFalse(otp.is_valid())

    def test_otp_validity_already_used(self):
        otp = OTPVerification.generate_otp(self.user, purpose="register")
        otp.is_used = True
        otp.save()
        self.assertFalse(otp.is_valid())


class AddressModelTestCase(TestCase):
    """Test suite for Address model logic."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="addressuser@example.com",
            name="Address User",
            password="password123"
        )

    def test_create_address_and_default_flag(self):
        addr1 = Address.objects.create(
            user=self.user,
            address_line1="123 Main St",
            city="Dhaka",
            state="Dhaka",
            is_default=True
        )
        self.assertTrue(addr1.is_default)
        self.assertEqual(str(addr1), "123 Main St, Dhaka, Dhaka")

        # Creating a second default address should unset default on first
        addr2 = Address.objects.create(
            user=self.user,
            address_line1="456 Park Rd",
            city="Dhaka",
            state="Dhaka",
            is_default=True
        )
        addr1.refresh_from_db()
        self.assertFalse(addr1.is_default)
        self.assertTrue(addr2.is_default)


class UserAPITestCase(APITestCase):
    """Test suite for User endpoints using DRF APITestCase."""

    def setUp(self):
        self.register_url = "/api/users/register/"
        self.verify_otp_url = "/api/users/verify_otp/"
        self.login_url = "/api/users/login/"
        self.sent_otp_pass_url = "/api/users/sentOtpForPasswordChange/"
        self.reset_password_otp_url = "/api/users/ChangePasswordOtpVerification/"
        self.me_url = "/api/users/me/"
        self.address_url = "/api/users/address/"

        self.user_data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "password123",
            "phone": "01700000000"
        }

    def test_user_registration_and_verification_flow(self):
        # 1. Register User
        res = self.client.post(self.register_url, self.user_data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("otp", res.data)

        user = User.objects.get(email=self.user_data["email"])
        self.assertFalse(user.is_active)

        otp_code = res.data["otp"]

        # 2. Verify OTP
        verify_data = {
            "email": self.user_data["email"],
            "code": otp_code
        }
        res_verify = self.client.post(self.verify_otp_url, verify_data)
        self.assertEqual(res_verify.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.is_active)

        # 3. Login User
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        res_login = self.client.post(self.login_url, login_data)
        self.assertEqual(res_login.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", res_login.data)
        self.assertIn("refresh_token", res_login.data)

    def test_login_inactive_user_fails(self):
        # Register user (is_active=False by default)
        self.client.post(self.register_url, self.user_data)

        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        res = self.client.post(self.login_url, login_data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sent_otp_for_password_change_authenticated(self):
        user = User.objects.create_user(
            email="passchange@example.com",
            name="Pass User",
            password="password123",
            is_active=True
        )
        self.client.force_authenticate(user=user)

        res = self.client.post(self.sent_otp_pass_url, {"email": user.email})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_change_password_with_otp_authenticated(self):
        user = User.objects.create_user(
            email="reset@example.com",
            name="Reset User",
            password="oldpassword123",
            is_active=True
        )
        self.client.force_authenticate(user=user)
        otp = OTPVerification.generate_otp(user, purpose="reset")

        reset_data = {
            "email": user.email,
            "otp": otp.code,
            "new_password": "newsecretpassword",
            "confirm_password": "newsecretpassword"
        }
        res = self.client.post(self.reset_password_otp_url, reset_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.check_password("newsecretpassword"))

    def test_me_endpoint(self):
        user = User.objects.create_user(
            email="me@example.com",
            name="Me User",
            password="password123",
            is_active=True
        )
        self.client.force_authenticate(user=user)

        # GET Profile
        res_get = self.client.get(self.me_url)
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)
        self.assertEqual(res_get.data["email"], "me@example.com")

        # PATCH Profile
        res_patch = self.client.patch(self.me_url, {"name": "Updated Me"})
        self.assertEqual(res_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(res_patch.data["name"], "Updated Me")

        # DELETE Profile
        res_delete = self.client.delete(self.me_url)
        self.assertEqual(res_delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(email="me@example.com").exists())

    def test_address_crud_operations(self):
        user = User.objects.create_user(
            email="addressapi@example.com",
            name="Address API User",
            password="password123",
            is_active=True
        )
        self.client.force_authenticate(user=user)

        # Add Address
        payload = {
            "address_line1": "789 High St",
            "city": "Sylhet",
            "state": "Sylhet"
        }
        res_add = self.client.post(self.address_url, payload)
        self.assertEqual(res_add.status_code, status.HTTP_201_CREATED)

        # Get Address list
        res_list = self.client.get(self.address_url)
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_list.data), 1)

        addr_id = res_list.data[0]["id"]

        # Update Address
        res_update = self.client.patch(self.address_url, {"id": addr_id, "city": "Chittagong"})
        self.assertEqual(res_update.status_code, status.HTTP_200_OK)

        # Delete Address
        res_delete = self.client.delete(self.address_url, {"id": addr_id}, format="json")
        self.assertEqual(res_delete.status_code, status.HTTP_200_OK)
