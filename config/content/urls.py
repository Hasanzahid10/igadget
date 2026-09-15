from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BannerViewSet, PromoSectionViewSet

router = DefaultRouter()
router.register(r'banners', BannerViewSet, basename='banner')
router.register(r'promo-sections', PromoSectionViewSet, basename='promo-section')

urlpatterns = [
    path('', include(router.urls)),
]