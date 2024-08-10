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
    # Retrieve the product or return a 404 error if it doesn't exist
    product = get_object_or_404(Product, id=id)
    categories = Category.objects.all()

    # Use raw SQL to find 4 random products from the same category, excluding the current product
    query = '''
        SELECT * FROM shop_product
        WHERE category_id = %s AND id != %s
        ORDER BY RANDOM()
        LIMIT 8
    '''
    related_products = Product.objects.raw(query, [product.category_id, product.id])

    context = {
        "product": product,
        "related_products": related_products,
        "categories": categories,
    }
    return render(request, "product_info.html", context)


def search_products(request):
    categories = Category.objects.all()
    category_id = request.GET.get('category', None)

    if category_id:
        selected_category = Category.objects.filter(id=category_id).first()
        if selected_category:
            products_filter = ProductsFilter(data=request.GET, queryset=Product.objects.filter(category=selected_category))
        else:
            products_filter = ProductsFilter(data=request.GET, queryset=Product.objects.all())
    else:
        products_filter = ProductsFilter(data=request.GET, queryset=Product.objects.all())

    context = {
        "products_filter": products_filter,
        "categories": categories,
    }
    return render(request, "search_products.html", context)


