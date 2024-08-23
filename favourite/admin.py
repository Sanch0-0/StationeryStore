from django.contrib import admin
from .models import Favourite, FavouriteProduct

@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'products_count', 'created_at')

@admin.register(FavouriteProduct)
class FavouriteProductAdmin(admin.ModelAdmin):
    list_display = ('favourite', 'product', 'quantity')
