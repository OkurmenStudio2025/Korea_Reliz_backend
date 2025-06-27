import requests
from django.utils.crypto import get_random_string
from django.utils import timezone
from .models import PaymentSession, Order, OrderItem
from decouple import config
import uuid
import logging


PAYLER_API_KEY = config('PAYLER_KEY')
PAYLER_HOST = config('PAYLER_HOST')

# Логирование
logger = logging.getLogger(__name__)

def generate_order_id():
    """Генерирует уникальный order_id для каждого платежа."""
    return str(uuid.uuid4())
    # return f"order_{get_random_string(12)}"

def check_payment_status(session_id, order_id):
    """
    Проверяет статус платежа по session_id.
    """
    url = f"https://{PAYLER_HOST}/gapi/GetStatus"
    data = {
        "key": PAYLER_API_KEY,
        "session_id": session_id,
        "order_id": order_id
    }
    response = requests.post(url, data=data)
    # print(response)
    response_data = response.json()
    
    # print(response)
    if response_data.get("status") == "Charged":
        # print(response_data)
        payment_session = PaymentSession.objects.get(session_id=session_id)
        payment_session.status = "completed"
        payment_session.save()
        return "completed"
    elif response_data.get("status") == "Rejected":
        payment_session = PaymentSession.objects.get(session_id=session_id)
        payment_session.status = "failed"
        payment_session.save()
        return "failed"
    else:
        return "pendingg"




def create_payment_session(account, products, total_amount):
    order_id = generate_order_id()  
    url = f"https://{PAYLER_HOST}/gapi/StartSession"
    

    product_names = ', '.join(product.title for product in products)
    data = {
        "key": PAYLER_API_KEY,
        "type": "OneStep",
        "order_id": order_id,
        "amount": int(total_amount * 100),  
        "currency": "KGS",
        "product": product_names,  
        "return_url_success": "https://koreacenter.kg/profile",
        "return_url_decline": "https://koreacenter.kg/profile",
    }

    response = requests.post(url, data=data)
    response_data = response.json()
    logger.info(f"Ответ от Payler для создания сессии: {response_data}")

    if response_data.get("session_id"):
        payment_session = PaymentSession.objects.create(
            account=account,
            session_id=response_data["session_id"],
            order_id=order_id,
            status="pending",
            valid_through=timezone.now() + timezone.timedelta(minutes=10),  
            amount=total_amount,
            currency="KGS",
        )
        
        payment_session.products.set(products)  
        payment_session.save()

        return payment_session
    else:
        raise Exception("Failed to create payment session")
    

def create_order_after_payment(client, products, total_amount, currency='сом'):
    order_id = str(uuid.uuid4()).replace("-", "").upper()[:12]
    order = Order.objects.create(
        order_id=order_id,
        client=client,
        total_amount=total_amount,
        currency=currency,
        status='paid',  
        client_phone=client.phone_number,
    )

    for product_data in products:
        OrderItem.objects.create(
            order=order,
            product=product_data['product'],
            quantity=product_data['quantity'],
            price=product_data['product'].price,
        )

    return order
