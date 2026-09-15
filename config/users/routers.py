from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

# Initialize DefaultRouter
router = DefaultRouter()

# Register the UserViewSet with the prefix 'users'
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Route for /api/user/login/ to UserViewSet.login action
    path('user/login/', UserViewSet.as_view({'post': 'login'}), name='user-login'),

    # Include all auto-generated routes from the router (e.g. /api/users/login/)
    path('', include(router.urls)),
]