from .models import Favourite

def favourite_info(request):
    count_of_products = 0  
    total_price = 0.0  

    if request.user.is_authenticated:
        favourite, created = Favourite.objects.get_or_create(user=request.user)

        count_of_products = favourite.products.count()  

        # Calculate the total price of the cart items
        total_price = sum(
            item.quantity * item.product.price_with_discount
            for item in favourite.favourite_items.all()
        )

    return {
        'count_of_favourite_products': count_of_products,
        'favourite_total_price': total_price,
    }
