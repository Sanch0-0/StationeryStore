from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, response
from .models import Cart, CartItem
from shop.models import Product


@login_required
def get_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_items_with_total = []
    total_quantity = 0
    for item in cart.cart_items.order_by("-id"):
        total = item.quantity * item.product.price_with_discount
        total_discounted_price = item.quantity * (item.product.price - item.product.price_with_discount)

        cart_items_with_total.append({
            'item': item,
            'product': item.product,
            'quantity': item.quantity,
            'price': item.product.price_with_discount,
            'total': total,
            'total_discounted_price': total_discounted_price,
        })
        total_quantity += item.quantity

    total_price = sum(item['total'] for item in cart_items_with_total)

    context = {
        'cart': cart,
        'cart_items_with_total': cart_items_with_total,
        'total_price': total_price,
        'cart_total_quantity': total_quantity,
        'cart_total_price': total_price,
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'total_quantity': total_quantity,
            'cart_total_price': total_price
        })
    return render(request, "cart.html", context)



@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
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

        return JsonResponse({'success': True, 'message': 'Product added to favourites!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



@login_required
def update_cart_item(request, product_id):

    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, id=product_id)

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


@login_required
def delete_cart_items(request):
    print(request.POST)
    if request.method == "POST":
        item_ids= request.POST.get("item_ids").split(",")
        CartItem.objects.filter(id__in=item_ids).delete()
    return response.HttpResponse(status=200)


@login_required
def checkout(request):
    return render(request, "checkout.html")
