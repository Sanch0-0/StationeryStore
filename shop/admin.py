from django.contrib import admin

from .models import Category, Product, Rating, Review
from image_cropping import ImageCroppingMixin


class ProductAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ['name', 'category', 'price_with_discount']
    list_filter = ['category']
    search_fields = ['name', 'description']
    fields = ['image', 'cropping', 'name', 'description', 'price', 'discount', 'category']

class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'value', 'created_at')  # Display these fields in the admin list view
    search_fields = ('user__username', 'product__name')  # Add search functionality
    list_filter = ('value', 'created_at')  # Add filter functionality by rating value and creation date

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'review', 'created_at')  # Display these fields in the admin list view
    search_fields = ('user__username', 'product__name', 'review')  # Add search functionality
    list_filter = ('rating', 'created_at')  # Add filter functionality by rating and creation date


admin.site.register(Rating, RatingAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
