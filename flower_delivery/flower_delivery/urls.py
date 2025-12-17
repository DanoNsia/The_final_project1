from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path("catalog/", include("catalog.urls", namespace="catalog")),
    path("orders/", include(('orders.urls', 'orders'), namespace="orders")),
    path("cart/", include("cart.urls")),
    path('', RedirectView.as_view(url='/catalog/')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)