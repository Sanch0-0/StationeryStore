from django.urls import path

from .views import (
    index,
    get_product_by_id,
    search_products,
)

urlpatterns = [
    path('', index, name='index'),
    path('product/<int:id>', get_product_by_id, name="get_product_by_id"),
    path('search/', search_products, name="search_products"),
]
