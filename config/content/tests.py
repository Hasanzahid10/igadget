from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Banner, PromoSection


class BannerModelTestCase(TestCase):
    """Test suite for Banner model logic."""

    def test_create_banner(self):
        banner = Banner.objects.create(
            title="Summer Sale",
            subtitle="Up to 50% Off",
            image_url="https://example.com/banner1.jpg",
            badge_text="HOT",
            display_order=1,
            is_active=True
        )
        self.assertEqual(str(banner), "Summer Sale")
        self.assertTrue(banner.is_active)
        self.assertEqual(banner.display_order, 1)

    def test_banner_ordering(self):
        b1 = Banner.objects.create(
            title="Banner 1",
            image_url="https://example.com/b1.jpg",
            display_order=10
        )
        b2 = Banner.objects.create(
            title="Banner 2",
            image_url="https://example.com/b2.jpg",
            display_order=1
        )
        banners = list(Banner.objects.all())
        self.assertEqual(banners, [b2, b1])


class PromoSectionModelTestCase(TestCase):
    """Test suite for PromoSection model logic."""

    def test_create_promo_section(self):
        promo = PromoSection.objects.create(
            title="Exclusive Deals",
            subtitle="Special prices for you",
            icon_url="https://example.com/icon.png",
            action_link="/deals/",
            type="exclusive_offer"
        )
        self.assertEqual(promo.title, "Exclusive Deals")
        self.assertEqual(str(promo), "Exclusive Offer - Exclusive Deals")


class BannerAPITestCase(APITestCase):
    """Test suite for Banner API endpoints."""

    def setUp(self):
        self.banners_url = "/api/content/banners/"
        self.active_banner = Banner.objects.create(
            title="Active Banner",
            image_url="https://example.com/active.jpg",
            is_active=True,
            display_order=1
        )
        self.inactive_banner = Banner.objects.create(
            title="Inactive Banner",
            image_url="https://example.com/inactive.jpg",
            is_active=False,
            display_order=2
        )

    def test_list_active_banners(self):
        res = self.client.get(self.banners_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Should only list active banners
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["title"], "Active Banner")

    def test_get_banner_detail(self):
        detail_url = f"{self.banners_url}{self.active_banner.id}/"
        res = self.client.get(detail_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], "Active Banner")

    def test_banner_read_only(self):
        # Attempting POST should return 405 Method Not Allowed
        res = self.client.post(self.banners_url, {"title": "New Banner", "image_url": "http://example.com/new.jpg"})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class PromoSectionAPITestCase(APITestCase):
    """Test suite for PromoSection API endpoints."""

    def setUp(self):
        self.promo_url = "/api/content/promo-sections/"
        self.exclusive_promo = PromoSection.objects.create(
            title="VIP Offer",
            subtitle="Exclusive to members",
            action_link="/vip/",
            type="exclusive_offer"
        )
        self.deal_promo = PromoSection.objects.create(
            title="Flash Sale",
            subtitle="Today only",
            action_link="/flash/",
            type="deal_of_day"
        )
        self.member_promo = PromoSection.objects.create(
            title="Member Perks",
            subtitle="Free Shipping",
            action_link="/perks/",
            type="member_benefits"
        )

    def test_list_promo_sections(self):
        res = self.client.get(self.promo_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)

    def test_exclusive_offer_endpoint(self):
        url = f"{self.promo_url}exclusive-offer/"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], "VIP Offer")
        self.assertEqual(res.data["type_display"], "Exclusive Offer")

    def test_deal_of_day_endpoint(self):
        url = f"{self.promo_url}deal-of-day/"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], "Flash Sale")
        self.assertEqual(res.data["type_display"], "Deal of the Day")

    def test_member_benefits_endpoint(self):
        url = f"{self.promo_url}member-benefits/"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], "Member Perks")
        self.assertEqual(res.data["type_display"], "Member Benefits")
