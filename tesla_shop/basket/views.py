from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Basket as BasketModel, BasketItem
from cards.models import Product
from .serializers import BasketSerializer

class DeleteBasketItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        try:
            basket = request.user.basket
            item = basket.items.get(product_id=product_id)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except BasketItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        except BasketModel.DoesNotExist:
            return Response({"error": "Basket not found"}, status=status.HTTP_404_NOT_FOUND)

class BasketView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            basket = request.user.basket
        except BasketModel.DoesNotExist:
            return Response({"error": "Basket not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BasketSerializer(basket, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get("product")
        quantity = request.data.get("quantity", 1)

        if not product_id:
            return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        if quantity < 1:
            return Response({"error": "Quantity must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        basket, _ = BasketModel.objects.get_or_create(user=request.user)
        basket_item, created = BasketItem.objects.get_or_create(basket=basket, product=product)

        if created:
            basket_item.quantity = quantity
        else:
            basket_item.quantity += quantity

        basket_item.save()

        serializer = BasketSerializer(basket, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class DeleteBasketView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            basket = request.user.basket
            item = basket.items.all()
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except BasketItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        except BasketModel.DoesNotExist:
            return Response({"error": "Basket not found"}, status=status.HTTP_404_NOT_FOUND)