from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_history_view, name='order-history'),
    path('chi-tiet-don-hang/', views.order_detail_view, name='order-detail'),
    path('order-success/', views.order_success_view, name='order-success'),
]
