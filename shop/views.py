from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseNotFound
# from django.core.paginator import Paginator

from .models import  Product, Category
from .filters import ProductsFilter


def index(request):
    # Using raw SQL for random selection
    random_products = Product.objects.raw('SELECT * FROM shop_product ORDER BY RANDOM() LIMIT 9')
    categories = Category.objects.all()

    context = {
        "products": random_products,
        "categories": categories,
    }
    return render(request, "home.html", context)


def get_product_by_id(request, id):
    try:
        product = get_object_or_404(Product, id=id)
    except Product.DoesNotExist:
        return HttpResponseNotFound("Product not found")

    context = {
        "product": product
    }
    return render(request, "product_info.html", context)


def search_products(request):
    categories = Category.objects.all()
    products_filter = ProductsFilter(data=request.GET, queryset=Product.objects.all())

    context = {
        "products_filter": products_filter,
        "categories": categories,
    }
    return render(request, "search_products.html", context)
