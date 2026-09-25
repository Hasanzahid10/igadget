from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='order')
router.register(r'orders', OrderViewSet, basename='order-alt')

urlpatterns = [
    path('', include(router.urls)),
]