from rest_framework import serializers
from .models import BasketItem, Basket
from cards.serializers import ProductSerializer

class BasketItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = BasketItem
        fields = ['quantity', 'product']

class BasketSerializer(serializers.ModelSerializer):
    items = BasketItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Basket
        fields = ['user', 'items', 'created_at', 'updated_at', 'total_price', 'total_item_count']