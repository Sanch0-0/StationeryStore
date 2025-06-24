from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from main.tasks import log_task


@shared_task
def send_checkout_email(email, subtotal_price, total_discount, total_price, total_quantity, count_of_products, order_date, personal_number):
    try:
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

        send_mail(
            subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=html_message
        )
    except Exception as e:
        log_task(f"Failed to send email to {email}: {e}", 'error')