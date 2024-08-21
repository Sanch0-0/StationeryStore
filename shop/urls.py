from django.urls import path

from .views import (
    index,
    get_product_by_id,
    search_products,
    delivery_policy,
    terms,
    privacy_policy,
    refund,
    about_us,
    contact_us
)

urlpatterns = [
    path('', index, name='index'),
    path('product/<int:id>', get_product_by_id, name="get_product_by_id"),
    path('search/', search_products, name="search_products"),
    path('delivery_policy/', delivery_policy, name='delivery_policy'),
    path('terms_conditions/', terms, name='terms'),
    path('privacy_policy/', privacy_policy, name='privacy_policy'),
    path('refund_return/', refund, name='refund'),
    path('about_us', about_us, name='about_us'),
    path('contact_us', contact_us, name='contact_us')
]
