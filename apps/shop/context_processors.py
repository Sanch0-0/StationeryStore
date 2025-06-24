from .models import Product

def top_rated_products(request):
    top_rated_products = Product.top_rated_products()
    return {
        'top_rated_products': top_rated_products,
    }
