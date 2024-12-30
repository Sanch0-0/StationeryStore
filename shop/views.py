from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import F
from django.db import models

from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from .models import Product, Category, ReviewRating
from .filters import ProductsFilter
from main.tasks import log_task


def index(request):
    log_task(f"User {request.user.username} accessed the Home page.", 'info')

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
    log_task(f"User {request.user.username} accessed the Product_Info page for Product ID {id}.", 'info')
    
    product = get_object_or_404(Product, id=id)
    categories = Category.objects.all()

    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                log_task(f"Received POST data: {request.POST}", 'debug')
                rating_value = int(request.POST.get('rating'))
                if rating_value < 1 or rating_value > 5:
                    log_task(f"User {request.user.username} submitted an invalid rating: {rating_value}.", 'warning')
                    return JsonResponse({'error': 'Invalid rating value.'}, status=400)

                review_rating, created = ReviewRating.objects.get_or_create(product=product, user=request.user)
                review_rating.rating = rating_value
                review_rating.save()

                new_average = product.review_ratings.aggregate(average_rating=models.Avg('rating'))['average_rating']
                log_task(f"User {request.user.username} submitted a rating of {rating_value} for Product ID {id}.", 'info')

                return JsonResponse({'success': True, 'new_average': new_average})
            except (ValueError, TypeError) as e:
                log_task(f"Failed to process rating submission for Product ID {id}. Error: {e}", 'error')
                return JsonResponse({'error': 'Invalid rating input.'}, status=400)
        else:
            log_task(f"User {request.user.username} made a non-AJAX POST request to Product ID {id}.", 'warning')
            review_text = request.POST.get('review')
            rating_value = int(request.POST.get('rating', 0))
            if review_text or rating_value:
                review_rating, created = ReviewRating.objects.update_or_create(
                    product=product,
                    user=request.user,
                    defaults={'review': review_text, 'rating': rating_value}
                )
                log_task(f"User {request.user.username} submitted a review for Product ID {id}.", 'info')
                return redirect(reverse('get_product_by_id', args=[product.id]))
            else:
                log_task(f"User {request.user.username} submitted an empty review for Product ID {id}.", 'warning')
                return JsonResponse({'error': 'Review text cannot be empty.'}, status=400)

    reviews = product.review_ratings.all()
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id).order_by('?')[:8]

    context = {
        "product": product,
        "related_products": related_products,
        "categories": categories,
        "reviews": reviews,
    }

    return render(request, "product_info.html", context)


def search_products(request):
    log_task(f"User {request.user.username} initiated a product search.", 'info')

    categories = Category.objects.all()
    category_id = request.GET.get('category', None)
    sort_by = request.GET.get('sort_by', None)

    log_task(f"Search parameters: category={category_id}, sort_by={sort_by}", 'debug')
    
    # Initial queryset with all products
    queryset = Product.objects.all()
    log_task(f"Initial product count: {queryset.count()}", 'debug')

    # Filter by category if provided
    if category_id:
        queryset = queryset.filter(category_id=category_id)
        log_task(f"User {request.user.username} filtered products by category ID {category_id}. Remaining products: {queryset.count()}", 'info')

    # Apply sorting based on user selection
    if sort_by == 'newest':
        queryset = queryset.order_by('-created_at')
        log_task(f"User {request.user.username} applied sorting: newest first.", 'info')
    elif sort_by == 'cheap_first':
        queryset = queryset.annotate(
            db_price_with_discount=F("price") - F("price") * F("discount") / 100
        ).order_by('db_price_with_discount')
        log_task(f"User {request.user.username} applied sorting: cheap first.", 'info')
    elif sort_by == 'expensive_first':
        queryset = queryset.annotate(
            db_price_with_discount=F("price") - F("price") * F("discount") / 100
        ).order_by('-db_price_with_discount')
        log_task(f"User {request.user.username} applied sorting: expensive first.", 'info')
    elif sort_by == 'random':
        queryset = queryset.order_by('?')
        log_task(f"User {request.user.username} applied sorting: random order.", 'info')

    # Apply additional filters from the ProductsFilter
    try:
        products_filter = ProductsFilter(data=request.GET, queryset=queryset)
        filtered_queryset = products_filter.qs
        log_task(f"User {request.user.username} applied additional filters. Remaining products: {filtered_queryset.count()}", 'info')
    except Exception as e:
        log_task(f"Error applying additional filters: {e}", 'error')
        filtered_queryset = queryset

    # Paginate the filtered queryset
    paginator = Paginator(filtered_queryset, 15)
    page_num = request.GET.get('page', 1)

    try:
        page_obj = paginator.get_page(page_num)
        log_task(f"Paginated products. Current page: {page_num}, Total pages: {paginator.num_pages}", 'info')
    except Exception as e:
        log_task(f"Pagination error: {e}", 'error')
        page_obj = paginator.get_page(1)

    context = {
        "products_filter": products_filter,
        "categories": categories,
        "page_obj": page_obj,
        'page_num': page_num
    }

    return render(request, "search_products.html", context)


def delivery_policy(request):
    log_task(f"User {request.user.username} accessed the Delivery Policy page.", 'info')
    return render(request, "delivery_policy.html")


def terms(request):
    log_task(f"User {request.user.username} accessed the Terms page.", 'info')
    return render(request, "terms.html")


def privacy_policy(request):
    log_task(f"User {request.user.username} accessed the Privacy Policy page.", 'info')
    return render(request, "privacy_policy.html")


def refund_policy(request):
    log_task(f"User {request.user.username} accessed the Refund Policy page.", 'info')
    return render(request, "refund_policy.html")


def about_us(request):
    log_task(f"User {request.user.username} accessed the About Us page.", 'info')
    return render(request, "about_us.html")


def contact_us(request):
    log_task(f"User {request.user.username} accessed the Contact Us page.", 'info')
    return render(request, "contact_us.html")
