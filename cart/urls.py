from django.urls import path

from .views import (
    get_cart,
    add_to_cart,
    update_cart_item,
    delete_from_cart,
    delete_cart_items,
)

urlpatterns = [
    path("", get_cart, name="get_cart"),
    path("add/<int:product_id>", add_to_cart, name="add_to_cart"),
    path('update-cart-item/<int:product_id>/', update_cart_item, name='update_cart_item'),
    path('delete-from-cart/<int:product_id>/', delete_from_cart, name='delete_from_cart'),
    path('delete-items/', delete_cart_items, name="delete_cart_items")
]
