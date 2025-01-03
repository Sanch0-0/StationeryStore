from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configure Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Stationery Store",
        default_version='v1',
        description="This is a simple practice-project which includes almost all tools a backend web-developer needs to know.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="fff.alex.er.fff@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
