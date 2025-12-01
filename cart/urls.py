from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('thanh-toan', views.checkout, name='checkout'),
]
