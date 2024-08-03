from django.urls import path

from .views import (
    index,
    get_product_by_id,
    get_all_products,
)

urlpatterns = [
    path('', index, name='index'),
    path('product/<int:id>', get_product_by_id, name="get_product_by_id"),
    path('products/all', get_all_products, name="get_all_products"),
]
