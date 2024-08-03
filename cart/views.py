from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from shop.models import Product

@login_required
def get_cart(request):
    # Получить или создать корзину пользователя
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Рассчитать сумму для каждого элемента корзины
    cart_items_with_total = []
    for item in cart.cart_items.all():
        total = item.quantity * item.product.price_with_discount
        cart_items_with_total.append({
            'product': item.product,
            'quantity': item.quantity,
            'price': item.product.price_with_discount,
            'total': total,
        })

    # Общая сумма корзины
    total_price = sum(item['total'] for item in cart_items_with_total)

    context = {
        'cart': cart,
        'cart_items_with_total': cart_items_with_total,
        'total_price': total_price,
    }
    return render(request, "cart.html", context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = request.GET.get("quantity", 1)

    # Получите или создайте корзину пользователя
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Попробуйте получить элемент корзины, или создайте новый, если его нет
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
    )

    # Обновите количество товара в корзине
    cart_item.quantity += int(quantity)
    cart_item.save()

    return redirect(request.META.get("HTTP_REFERER", "/"))
