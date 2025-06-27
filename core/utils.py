from django.conf import settings
from django.core.mail import send_mail


# def send_message(subject, message, recipient_list, html_message=None):
#     email_from = settings.EMAIL_HOST_USER
    
#     send_mail(
#         subject,
#         message,
#         email_from,
#         recipient_list,
#         html_message=html_message
#     )