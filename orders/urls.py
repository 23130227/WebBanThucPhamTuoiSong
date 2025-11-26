from django.urls import path
from . import views

urlpatterns = [
    path('order-history/', views.order_history, name='order-history'),
    path('order-history/order-detail', views.order_detail, name='order-detail'),
    path('order-success', views.order_success, name='order-success'),
]
