from django.contrib import admin

from .models import Cart, CartItem

class CartItemInline(admin.StackedInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "created_at"]
    list_display_links = ["id", "user", "created_at"]
    search_fields = ["user__email", "user__full_name"]
    inlines = [CartItemInline]