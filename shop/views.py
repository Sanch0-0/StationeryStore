from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseNotFound
# from django.core.paginator import Paginator

from .models import  Product, Category
import random


def index(request):
    products = list(Product.objects.all())
    random_products = random.sample(products, min(len(products), 9))
    categories = Category.objects.all()

    context = {
        "products": random_products,
        "categories": categories,
    }
    return render(request, "products_list.html", context)


def get_product_by_id(request, id):
    try:
        product = get_object_or_404(Product, id=id)
    except Product.DoesNotExist:
        return HttpResponseNotFound("Product not found")

    context = {
        "product": product
    }
    return render(request, "product_info.html", context)


def get_all_products(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    context = {
        "products": products,
        "categories": categories,
    }
    return render(request, "products.html", context)
