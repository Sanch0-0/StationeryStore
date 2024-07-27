from django.urls import path

from .views import (
    index,
    get_product_by_id
)

urlpatterns = [
    path('', index, name='index'),
    path('products/<int:id>', get_product_by_id, name="get_product_by_id")
]
