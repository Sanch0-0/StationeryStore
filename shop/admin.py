from django.contrib import admin

from .models import Category, Product
from image_cropping import ImageCroppingMixin


class ProductAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ['name', 'category', 'price_with_discount']
    list_filter = ['category']
    search_fields = ['name', 'description']
    fields = ['image', 'cropping', 'name', 'description', 'price', 'discount', 'category']

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
