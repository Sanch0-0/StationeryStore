from django.contrib import admin

# Register your models here.
from .models import Category, Clothes

admin.site.register(Category)
admin.site.register(Clothes)
