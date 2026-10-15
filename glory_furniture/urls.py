from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.core.views import robots_txt_view, sitemap_xml_view

urlpatterns = [
    path('robots.txt', robots_txt_view, name='robots_txt'),
    path('sitemap.xml', sitemap_xml_view, name='sitemap_xml'),
    path('django-admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('', include('apps.store.urls')),
    path('', include('apps.bookings.urls')),
    path('', include('apps.custom_orders.urls')),
    path('', include('apps.accounts.urls')),
    path('payments/', include('apps.payments.urls')),
]

from django.views.static import serve
from django.urls import re_path

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
