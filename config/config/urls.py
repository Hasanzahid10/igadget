from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.routers')),
    path('api/catalog/', include('catalog.routers')),
    path('api/content/', include('content.urls')),
    path('api/cart/', include('cart.routers')),
    path('api/orders/', include('orders.routers')),
    path('api/wishlist/', include('wishlist.routers')),
    path('api/admin/', include('admin_panel.routers')),
]
