from .models import Category, Product, ReviewRating
from image_cropping import ImageCroppingMixin
from django.shortcuts import redirect
from django.contrib import admin
from django import forms


@admin.register(Product)
class ProductAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ('name', 'category', 'price_with_discount', 'brand')
    list_filter = ('category', 'price', 'brand')
    search_fields = ('name', 'description', 'brand')
    fields = ('image', 'name', 'description', 'price', 'discount', 'category', 'brand')

    def get_fields(self, request, obj=None):
        fields = ['image', 'name', 'description', 'price', 'discount', 'category', 'brand']
        if obj:  #(редактирование)
            fields.insert(1, 'cropping')  # вставляем после image
        return fields

    def response_add(self, request, obj, post_url_continue=None):
        return redirect(f"/admin/shop/product/{obj.pk}/change/")

@admin.register(ReviewRating)
class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'review', 'created_at')
    list_filter = ('product', 'user', 'created_at', 'product__brand')  
    search_fields = ('user__email', 'product__name', 'review', 'product__brand') 
    readonly_fields = ('created_at',)

    def get_readonly_fields(self, request, obj=None):
        if obj: 
            return self.readonly_fields + ('user', 'product')
        return self.readonly_fields


admin.site.register(Category)

