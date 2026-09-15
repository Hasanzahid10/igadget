from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, BrandViewSet, ProductViewSet

router = DefaultRouter()

# register viewsets 
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'brand', BrandViewSet, basename='brand')
router.register(r'products', ProductViewSet, basename='products')

urlpatterns = [
    path('', include(router.urls)),
]