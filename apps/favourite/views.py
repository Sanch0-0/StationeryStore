from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, response
from .models import Favourite, FavouriteProduct
from apps.shop.models import Product
from core.tasks import log_task


def get_favourite(request):
    log_task(f"User {request.user.username} accessed the Favourite page.", 'info')
    favourite, created = Favourite.objects.get_or_create(user=request.user)

    favourite_items_with_total = []
    total_quantity = 0

    for item in favourite.favourite_items.order_by("-id"):
        total = item.quantity * item.product.price_with_discount
        total_discounted_price = item.quantity * (item.product.price - item.product.price_with_discount)

        favourite_items_with_total.append({
            'item': item,
            'product': item.product,
            'quantity': item.quantity,
            'price': item.product.price_with_discount,
            'total': total,
            'total_discounted_price': total_discounted_price,
        })
        log_task(f"Processed favourite item {item.id}: quantity={item.quantity}, total={total}.", 'debug')
        total_quantity += item.quantity

    total_price = sum(item['total'] for item in favourite_items_with_total)

    context = {
        'favourite': favourite,
        'favourite_items_with_total': favourite_items_with_total,
        'total_price': total_price,
        'favourite_total_quantity': total_quantity,
        'favourite_total_price': total_price,
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'total_quantity': total_quantity,
            'cart_total_price': total_price
        })

    return render(request, "favourite.html", context)



def add_to_favourite(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = request.POST.get("quantity", 1)

        favourite, created = Favourite.objects.get_or_create(user=request.user)

        favourite_item, created = FavouriteProduct.objects.get_or_create(
            favourite=favourite,
            product=product,
        )

        if created:
            favourite_item.quantity = int(quantity)
            log_task(f"User {request.user.username} added new product {product.id} to favourite list with quantity {quantity}.", 'info')
        else:
            favourite_item.quantity += int(quantity)
            log_task(f"User {request.user.username} updated product {product.id} quantity to {favourite_item.quantity} in the favourite list.", 'info')
        favourite_item.save()

        return JsonResponse({'success': True, 'message': 'Product added to favourites!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



def update_favourite_item(request, product_id):

    favourite = get_object_or_404(Favourite, user=request.user)
    favourite_item = get_object_or_404(FavouriteProduct, favourite=favourite, id=product_id)

    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', 1))
        favourite_item.quantity = new_quantity
        favourite_item.save()

    item_total = favourite_item.quantity * favourite_item.product.price_with_discount
    favourite_total = sum(item.quantity * item.product.price_with_discount for item in favourite.favourite_items.all())

    return JsonResponse({
        'item_total': item_total,
        'favourite_total': favourite_total,
    })


def delete_from_favourite(request, product_id):
    favourite = get_object_or_404(Favourite, user=request.user)
    favourite_item = get_object_or_404(FavouriteProduct, favourite=favourite, product_id=product_id)
    favourite_item.delete()

    log_task(f"User {request.user.username} deleted a product: {product_id} from favourite list.", 'info')
    return redirect(request.META.get("HTTP_REFERER", "/"))


def delete_favourite_items(request):
    if request.method == "POST":
        item_ids = request.POST.get("item_ids").split(",")
        deleted_count, _ = FavouriteProduct.objects.filter(id__in=item_ids).delete()
            
        log_task(f'The favourite list has been cleared of {deleted_count} products.', 'info')
    return response.HttpResponse(status=200)
