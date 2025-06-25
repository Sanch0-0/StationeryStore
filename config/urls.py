from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

#Todo поправить урлы
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("apps.shop.urls")),
    path('user/', include('apps.users.urls')),
    path('cart/', include("apps.cart.urls")),
    path('favourite/', include('apps.favourite.urls')),
    # path('api/', include('api.urls')),
    path("admin/doc/", TemplateView.as_view(template_name="admin_doc.html"), name="django-admindocs-docroot"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)