import requests
from rest_framework import generics
from rest_framework.generics import UpdateAPIView, DestroyAPIView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.views import APIView
from cards.models import Product
from account.models import CustomUser
from .utils import create_payment_session, check_payment_status
from .models import  Order
from .serializers import OrderSerializer, OrderCreateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response 
from decouple import config
import logging

PAYLER_HOST = config('PAYLER_HOST')
PAYLER_KEY = config('PAYLER_KEY')


logger = logging.getLogger(__name__)

class StartPaymentSessionView(APIView):
    def post(self, request):
        product_ids = request.data.get("product_ids", [])
        account = get_object_or_404(CustomUser, id=request.user.id)

        products = Product.objects.filter(id__in=product_ids)
        if not products:
            return JsonResponse({"error": "No active products found"}, status=400)

        total_amount = sum(product.price for product in products)

        try:
            payment_session = create_payment_session(account, products, total_amount)
            pay_url = f"https://{PAYLER_HOST}/gapi/Pay?session_id="
            return JsonResponse({"pay_url": pay_url,
                                 "payment_session": payment_session.session_id,
                                 "order_id": payment_session.order_id})


        except Exception as e:
            return JsonResponse({"error": str(e)})


class PaymentStatusView(APIView):
    def get(self, request, session_id, order_id):
        status = check_payment_status(session_id, order_id)
        # print(status)
        return JsonResponse({"status": status})


class FindSessionView(APIView):
    def get(self, request, order_id):
        url = f"https://{PAYLER_HOST}/gapi/FindSession"
        params = {"key": PAYLER_KEY, "order_id": order_id}

        logger.info(f"Отправка запроса для поиска сессии с order_id={order_id}")

        try:
            response = requests.get(url, params=params)
            response_data = response.json()
            
            logger.info(f"Получен ответ: {response_data}")

            if response.status_code == 200:
                return JsonResponse(response_data, status=200)
            else:
                logger.error(f"Ошибка при поиске сессии: {response_data.get('message', 'Неизвестная ошибка')}")
                return JsonResponse({"error": response_data.get("message", "Ошибка при поиске сессии")}, status=response.status_code)

        except requests.RequestException as e:
            logger.error(f"Ошибка запроса к Payler API: {str(e)}")
            return JsonResponse({"error": "Ошибка запроса к Payler API"}, status=500)


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

class AdminOrderListView(generics.ListAPIView):
    """
    Эндпоинт для администратора — получить все заказы.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':  
            return Order.objects.all()
        return Order.objects.none()  


            
from rest_framework.exceptions import NotFound, PermissionDenied

class LastOrderDetailView(generics.ListAPIView):
    """
    Эндпоинт для клиента — получить последний заказ.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        order = Order.objects.filter(client=user)
        
        if not order:
            print(order)
            raise NotFound("Последний заказ не найден.")
        
        return order

class OrderPatchView(UpdateAPIView):
    """
    Эндпоинт для частичного обновления заказа клиента.
    """
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_object(self):
        order = super().get_object()
        if not self.request.user.role == "admin":
            raise PermissionDenied("Вы не можете изменять этот заказ.")

        return order

    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
class OrderDeleteView(generics.DestroyAPIView):
    """
    Эндпоинт для удаления заказа клиента.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.role == "admin":
            return Order.objects.all()

        return Order.objects.filter(client=self.request.user)

    def get_object(self):
        order = super().get_object()
        if self.request.user.role != "admin" and order.client != self.request.user:
            raise PermissionDenied("Вы не можете удалить этот заказ.")

        return order