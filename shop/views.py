from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotFound, JsonResponse
from django.core.paginator import Paginator
from django.db.models import F, Avg
from django.db import models, transaction

from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from .models import Product, Category, Rating, Review
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

    if request.method == 'POST':
        user = request.user

        # Handle AJAX request for rating
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                rating_value = int(request.POST.get('rating'))
                if rating_value < 1 or rating_value > 5:
                    return JsonResponse({'error': 'Invalid rating value.'}, status=400)

                # Get or create the rating
                rating, created = Rating.objects.get_or_create(product=product, user=user)
                rating.value = rating_value
                rating.save()

                # Recalculate average rating
                new_average = product.ratings.aggregate(average_rating=models.Avg('value'))['average_rating']

                return JsonResponse({'success': True, 'new_average': new_average})
            except (ValueError, TypeError):
                return JsonResponse({'error': 'Invalid rating input.'}, status=400)

        # Handle review form submission (standard POST request)
        else:
            review_text = request.POST.get('review')
            rating_value = int(request.POST.get('rating', 0))
            if review_text or rating_value:
                # Create or update the review
                review, created = Review.objects.update_or_create(
                    product=product,
                    user=user,
                    defaults={'review': review_text, 'rating': rating_value}
                )
                # Redirect to avoid resubmission
                return redirect(reverse('get_product_by_id', args=[product.id]))
            else:
                return JsonResponse({'error': 'Review text cannot be empty.'}, status=400)

    # Retrieve all reviews for the product
    reviews = product.reviews.all()

    # ORM query to get related products
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id).order_by('?')[:8]

    context = {
        "product": product,
        "related_products": related_products,
        "categories": categories,
        "reviews": reviews,
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


def delivery_policy(request):
    return render(request, "delivery_policy.html")


def terms(request):
    return render(request, "terms.html")


def privacy_policy(request):
    return render(request, "privacy_policy.html")


def refund_policy(request):
    return render(request, "refund_policy.html")


def about_us(request):
    return render(request, "about_us.html")


def contact_us(request):
    return render(request, "contact_us.html")
