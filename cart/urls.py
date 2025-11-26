from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart, name='cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
]
