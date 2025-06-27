from celery import shared_task
from .utils import send_sms

@shared_task
def send_activation_code(verification_code, phone_number):
    message = 'print'
    response = send_sms(phone_number, verification_code)
    return response

