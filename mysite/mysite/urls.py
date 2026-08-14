# mysite/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from shopapp.sitemap import ShopSitemap

sitemaps = {
    'shop': ShopSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shop/', include('shopapp.urls')),
    path('accounts/', include('myauth.urls')),  # было myauth/, стало accounts/
    path('', RedirectView.as_view(url='/shop/', permanent=False)),
    # path('blog/', include('blogapp.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
