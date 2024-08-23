from django.urls import path
from .views import (
    get_favourite,
    add_to_favourite,
    update_favourite_item,
    delete_from_favourite,
    delete_favourite_items,
)

urlpatterns = [
    path("", get_favourite, name='get_favourite'),
    path('add/<int:product_id>/', add_to_favourite, name='add_to_favourite'),
    path('update-favourite-item/<int:product_id>/', update_favourite_item, name='update_favourite_item'),
    path('delete-from-favouirite/<int:product_id>/', delete_from_favourite, name='delete_from_favourite'),
    path('delete-items/', delete_favourite_items, name='delete_favourite_items'),
]
