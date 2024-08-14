from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from shop.models import Product


@login_required
def get_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_items_with_total = []
    for item in cart.cart_items.all():
        total = item.quantity * item.product.price_with_discount
        cart_items_with_total.append({
            'product': item.product,
            'quantity': item.quantity,
            'price': item.product.price_with_discount,
            'total': total,
        })

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
    quantity = request.POST.get("quantity", 1)

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
    )

    if created:
        cart_item.quantity = int(quantity)
    else:
        cart_item.quantity += int(quantity)
    cart_item.save()

    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def update_cart_item(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)

    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', 1))
        cart_item.quantity = new_quantity
        cart_item.save()

        item_total = cart_item.quantity * cart_item.product.price_with_discount
        cart_total = sum(item.quantity * item.product.price_with_discount for item in cart.cart_items.all())

        return JsonResponse({
            'item_total': item_total,
            'cart_total': cart_total,
        })


@login_required
def delete_from_cart(request, product_id):
    cart = Cart.objects.get(user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    cart_item.delete()
    return redirect(request.META.get("HTTP_REFERER", "/"))


