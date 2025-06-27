from django.urls import path
from .views import BasketView, DeleteBasketItemView, DeleteBasketView

urlpatterns = [
    path('basket/', BasketView.as_view(), name='basket'),  # URL to view the basket
    path('basket/item/<int:product_id>/', DeleteBasketItemView.as_view(), name='delete_basket_item'),
    path('basket/delete/', DeleteBasketView.as_view(), name='basket-delete')

]