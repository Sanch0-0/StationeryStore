from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseNotFound
# from django.core.paginator import Paginator

from .models import  Product, Category


def index(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    context = {
        "products": products,
        "categories": categories,
    }
    return render(request, "products_list.html", context)


def get_product_by_id(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return HttpResponseNotFound("Product not found")

    context = {
        "product": product
    }
    return render(request, "product_info.html", context)
