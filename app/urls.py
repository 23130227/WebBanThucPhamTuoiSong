from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('product-single/', views.product_single, name='product-single'),
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),
    path('blog/blog-single/', views.blog_single, name='blog-single'),
    path('cart/', views.cart, name='cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('contact/', views.contact, name='contact'),
    path('shop/', views.shop, name='shop'),
    path('wishlist/', views.wishlist, name='wishlist'),
]
