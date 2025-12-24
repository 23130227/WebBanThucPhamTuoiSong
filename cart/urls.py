from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:product_id>/', views.update_cart, name='update_cart'),
]
