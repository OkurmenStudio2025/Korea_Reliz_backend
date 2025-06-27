from rest_framework import serializers
from .models import PaymentSession, Order, OrderItem, Order
from cards.models import Product 


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.title')
    
    class Meta:
        model = OrderItem
        fields = ['product_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    client_name = serializers.SerializerMethodField()
    client_phone = serializers.CharField(source='client.phone_number')

    def get_client_name(self, obj):
        """Объединяет имя и фамилию клиента."""
        return f"{obj.client.first_name} {obj.client.last_name}".strip()
    class Meta:
        model = Order
        fields = [
            'id',
            'order_id',
            'order_date',
            'total_amount',
            'currency',
            'status',
            'client_name',
            'client_phone',
            'items'
        ]

class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']  

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ['order_id', 'total_amount', 'currency', 'items']

    def validate_order_id(self, value):
        if Order.objects.filter(order_id=value).exists():
            raise serializers.ValidationError("Order ID must be unique.")
        return value


    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        phone_number = user.phone_number  
        validated_data.pop('client', None)
        order = Order.objects.create(client=user, client_phone=phone_number, **validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order
