from django.conf.urls.static import static
from .yasg import urlpatterns as doc_urls
from django.urls import path, include
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.shop.urls')),
    path('user/', include('apps.users.urls')),
    path('cart/', include('apps.cart.urls')),
    path('favourite/', include('apps.favourite.urls')),
    path("admin/doc/", TemplateView.as_view(template_name="admin_doc.html"), name="django-admindocs-docroot"),

    path('api/v1/', include('apps.shop.api.urls')),
    path('api/v1/', include('apps.users.api.urls')),
    path('api/v1/', include('apps.cart.api.urls')),
    path('api/v1/', include('apps.favourite.api.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += doc_urls