"""
URL Configuration for Order API
"""
from django.urls import path
from api.views.order import (
    OrderListView,
    OrderDetailView,
    CreateOrderView,
    CancelOrderView,
)

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('create/', CreateOrderView.as_view(), name='order-create'),
    path('<str:order_number>/', OrderDetailView.as_view(), name='order-detail'),
    path('<str:order_number>/cancel/', CancelOrderView.as_view(), name='order-cancel'),
]
