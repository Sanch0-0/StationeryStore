from .models import Cart 

def cart_info(request):
    count_of_products = 0  
    total_price = 0.0  

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)

        count_of_products = cart.products.count()  

        # Calculate the total price of the cart items
        total_price = sum(
            item.quantity * item.product.price_with_discount
            for item in cart.cart_items.all()
        )

    return {
        'count_of_products': count_of_products,
        'cart_total_price': total_price,
    }
