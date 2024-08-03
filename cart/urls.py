from django.urls import path

from .views import (
    get_cart,
    add_to_cart,
)

urlpatterns = [
    path("", get_cart, name="get_cart"),
    path("add/<int:product_id>", add_to_cart, name="add_to_cart"),
]