from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseNotFound
from django.core.paginator import Paginator
from django.db.models import F

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Product, Category, Rating
from .filters import ProductsFilter


def index(request):
    newest_products = Product.objects.raw('SELECT * FROM shop_product ORDER BY created_at DESC LIMIT 9')
    categories = Category.objects.all()
    top_rated_products = Product.top_rated_products()

    context = {
        "products": newest_products,
        "categories": categories,
        "top_rated_products": top_rated_products,
    }
    return render(request, "home.html", context)


@csrf_exempt
def get_product_by_id(request, id):
    product = get_object_or_404(Product, id=id)
    categories = Category.objects.all()

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        rating_value = int(request.POST.get('rating'))
        user = request.user

        # Get or create the rating
        rating, created = Rating.objects.get_or_create(product=product, user=user)
        rating.value = rating_value
        rating.save()

        # Recalculate average rating
        new_average = product.average_rating

        return JsonResponse({'success': True, 'new_average': new_average})

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
    sort_by = request.GET.get('sort_by', None)

    # Initial queryset with all products
    queryset = Product.objects.all()

    # Filter by category if provided
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    # Apply sorting based on user selection
    if sort_by == 'newest':
        queryset = queryset.order_by('-created_at')
    elif sort_by == 'cheap_first':
        queryset = queryset.annotate(
            db_price_with_discount=F("price") - F("price") * F("discount") / 100
        ).order_by('db_price_with_discount')
    elif sort_by == 'expensive_first':
        queryset = queryset.annotate(
            db_price_with_discount=F("price") - F("price") * F("discount") / 100
        ).order_by('-db_price_with_discount')
    elif sort_by == 'random':
        queryset = queryset.order_by('?')

    # Apply additional filters from the ProductsFilter
    products_filter = ProductsFilter(data=request.GET, queryset=queryset)
    filtered_queryset = products_filter.qs

    # Paginate the filtered queryset
    paginator = Paginator(filtered_queryset, 15) 
    page_num = request.GET.get('page', 1) 
    page_obj = paginator.get_page(page_num)

    context = {
        "products_filter": products_filter,
        "categories": categories,
        "page_obj": page_obj,
        'page_num': page_num
    }
    return render(request, "search_products.html", context)


