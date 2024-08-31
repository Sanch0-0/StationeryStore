from django.contrib import admin
from django import forms

from .models import Category, Product, ReviewRating
from image_cropping import ImageCroppingMixin


class ProductAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ['name', 'category', 'price_with_discount']
    list_filter = ['category']
    search_fields = ['name', 'description']
    fields = ['image', 'cropping', 'name', 'description', 'price', 'discount', 'category']

class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'review', 'created_at')
    list_filter = ('product', 'user', 'created_at')
    search_fields = ('user__email', 'product__name', 'review')
    readonly_fields = ('created_at',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('user', 'product')
        return self.readonly_fields

admin.site.register(ReviewRating, ReviewRatingAdmin)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
