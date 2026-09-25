from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WishlistViewSet

router = DefaultRouter()
router.register(r'', WishlistViewSet, basename='wishlist')
router.register(r'wishlist', WishlistViewSet, basename='wishlist-alt')

urlpatterns = [
    path('', include(router.urls)),
]