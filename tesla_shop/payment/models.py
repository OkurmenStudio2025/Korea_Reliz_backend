from django.db import models
from cards.models import Product  
from django.contrib.auth import get_user_model
from account.models import CustomUser
from django.utils import timezone
import uuid

User = get_user_model()

class PaymentSession(models.Model):
    account = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE, related_name="payment_sessions")  
    products = models.ManyToManyField(Product, related_name='payment_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    order_id = models.CharField(max_length=100, unique=True) 
    valid_through = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PaymentSession {self.session_id} for {self.account.first_name}"
    

class Order(models.Model):
    STATUS_CHOICES = [
        ('Отправлен', 'Отправлен'),
        ('Доставлен', 'Доставлен')
    ]
    order_id = models.CharField(max_length=100, unique=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='сом')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Отправлен')
    client_phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.client.get_full_name()}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  

    def __str__(self):
        return f"{self.product.title} x {self.quantity} in Order {self.order.order_id}"
