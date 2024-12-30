from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import JsonResponse, response
from django.contrib import messages
from django.utils import timezone

from .models import Cart, CartItem
from shop.models import Product
from users.models import User

from .tasks import send_checkout_email
from main import utils
from main.tasks import log_task
import secrets
import string



@login_required
def get_cart(request):
    log_task(f"User {request.user.username} accessed the Cart page.", 'info')
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
        log_task(f"Processed cart item {item.id}: quantity={item.quantity}, total={total}.", 'debug')
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
            log_task(f"User {request.user.username} added new product {product.id} to cart with quantity {quantity}.", 'info')
        else:
            cart_item.quantity += int(quantity)
            log_task(f"User {request.user.username} updated product {product.id} quantity to {cart_item.quantity} in the cart.", info)
        cart_item.save()

        # Calculate the total number of products in the cart and the total price
        count_of_products = cart.products.count()
        total_price = sum(
            item.quantity * item.product.price_with_discount
            for item in cart.cart_items.all()
        )

        return JsonResponse({
            'success': True,
            'message': 'Product added to cart!',
            'count_of_products': count_of_products,
            'cart_total_price': f'{total_price:.2f}'
        })

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})




@login_required
def update_cart_item(request, product_id):

    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, id=product_id)

    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', 1))
        cart_item.quantity = new_quantity
        cart_item.save()
        log_task(f"Cart for user {request.user.username} has been updated.", 'info')

    item_total = cart_item.quantity * cart_item.product.price_with_discount
    cart_total = sum(item.quantity * item.product.price_with_discount for item in cart.cart_items.all())

    log_task(f"Total items in {request.user.username}'s cart: {cart_total}.", 'debug')

    return JsonResponse({
        'item_total': item_total,
        'cart_total': cart_total,
    })

@login_required
def delete_from_cart(request, product_id):
    cart = Cart.objects.get(user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    cart_item.delete()

    log_task(f"User {request.user.username} deleted a product: {product_id} from cart.", 'info')
    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def delete_cart_items(request):
    if request.method == "POST":
        item_ids = request.POST.get("item_ids").split(",")
        deleted_count, _ = CartItem.objects.filter(id__in=item_ids).delete()
            
        log_task(f'The cart has been cleared of {deleted_count} products.', 'info')
    return HttpResponse(status=200)


def get_cart_items(user):
    try:
        cart = Cart.objects.get(user=user)  #ForeignKey from Cart to User
        return cart.cart_items.all()
    except Cart.DoesNotExist:
        log_task(f"Cart for user {user.username} doesn't exist!", 'error')
        return []


@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_items_with_total = []
    total_quantity = 0
    total_discount = 0
    subtotal_price = 0
    count_of_products = 0
    order_date = timezone.now()

    for item in cart.cart_items.order_by("-id"):
        product = item.product
        price = product.price
        price_with_discount = product.price_with_discount
        total = item.quantity * price_with_discount

        item_discount = item.quantity * (price - price_with_discount)
        total_discount += item_discount

        if product.discount > 0:
            subtotal_price += item.quantity * price
        else:
            subtotal_price += total

        cart_items_with_total.append({
            'item': item,
            'product': product,
            'quantity': item.quantity,
            'price': price_with_discount,
            'total': total,
            'total_discounted_price': item_discount,
        })

        total_quantity += item.quantity

    total_price = sum(item['total'] for item in cart_items_with_total)
    count_of_products = cart.products.count()

    context = {
        'cart_items_with_total': cart_items_with_total,
        'total_price': total_price,
        'cart_total_quantity': total_quantity,
        'total_discount': total_discount,
        'subtotal_price': subtotal_price,
    }

    if request.method == 'POST':
        full_name = request.POST.get('full-name')
        credit_card_num = request.POST.get('credit-card-num')
        cvv = request.POST.get('cvv')

        if full_name and credit_card_num and cvv:
            emails = User.objects.values_list("email", flat=True)

            def generate_personal_code(length=16):
                characters = string.ascii_letters + string.digits
                return ''.join(secrets.choice(characters) for _ in range(length))
                log_task(f"Personal code for {request.user.name} has been generated", 'info')

            messages.success(request, "The payment was successful!")
            personal_number = generate_personal_code()

            log_task(f"Checkout successful for user {request.user.email}, sending emails...", 'info')

            for email in emails:
                subject = "Checkout Receipt"

                html_message = render_to_string('checkout_message.html', {
                    'email': email,
                    'subtotal_price': subtotal_price,
                    'total_discount': total_discount,
                    'total_price': total_price,
                    'cart_total_quantity': total_quantity,
                    'count_of_products': count_of_products,
                    'order_date': order_date,
                    'personal_number': personal_number
                })

                utils.send_message(
                    subject=subject,
                    message=None,
                    recipient_list=[email],
                    html_message=html_message
                )

                log_task(f"Checkout email sent to {email}.", 'info')

        else:
            log_task("Error: Incorrect data provided during checkout.", 'error')

    return render(request, "checkout.html", context)
