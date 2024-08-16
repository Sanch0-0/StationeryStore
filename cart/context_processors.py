from .models import Cart

def cart_info(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        total_quantity = sum(item.quantity for item in cart.cart_items.all())
        total_price = sum(item.quantity * item.product.price_with_discount for item in cart.cart_items.all())
    else:
        total_quantity = 0
        total_price = 0.0

    return {
        'cart_total_quantity': total_quantity,
        'cart_total_price': total_price,
    }