from django.contrib import admin
from django.urls import path, include 
from django.conf import settings
from django.conf.urls.static import static

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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

