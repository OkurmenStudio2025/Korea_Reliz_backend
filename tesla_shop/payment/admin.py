from django.contrib import admin
from .models import PaymentSession, Order, OrderItem
# Register your models here.
admin.site.register(PaymentSession)
admin.site.register(Order)
admin.site.register(OrderItem)
