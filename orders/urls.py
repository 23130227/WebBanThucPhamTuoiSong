from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_history, name='order-history'),
    path('chi-tiet-don-hang/', views.order_detail, name='order-detail'),
    path('order-success/', views.order_success, name='order-success'),
]
