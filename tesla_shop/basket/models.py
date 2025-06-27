from django.db import models
from django.conf import settings
from cards.models import Product

class Basket(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

    @property
    def total_item_count(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f"Basket of {self.user.phone_number} - Total Price: {self.total_price}, Total Items: {self.total_item_count}"

class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.title} (x{self.quantity})"