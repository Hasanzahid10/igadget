from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminCategoryViewSet,
    AdminProductViewSet,
    AdminProductImageViewSet,
    AdminOrderViewSet
)

router = DefaultRouter()
router.register(r'categories', AdminCategoryViewSet, basename='admin-categories')
router.register(r'products', AdminProductViewSet, basename='admin-products')
router.register(r'product-images', AdminProductImageViewSet, basename='admin-product-images')
router.register(r'orders', AdminOrderViewSet, basename='admin-orders')

urlpatterns = [
    path('', include(router.urls)),
]