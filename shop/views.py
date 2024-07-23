from django.shortcuts import render
from django.http import HttpResponseNotFound
# from django.core.paginator import Paginator

from .models import  Product


def index(request):
    return render(request, "home.html")


def get_product_by_id(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return HttpResponseNotFound("Products not found")

    context = {
        "product": product
    }
    return render(request, "product_ifno.html", context)
