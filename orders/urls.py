from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_history_view, name='order_history'),
    path('order-detail/', views.order_detail_view, name='order_detail'),
    path('order-success/', views.order_success_view, name='order_success'),
]
