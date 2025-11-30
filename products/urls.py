from django.urls import path
from . import views

urlpatterns = [
    path('shop/product-single/', views.product_single, name='product-single'),
    path('shop/', views.shop, name='shop'),
    path('search-results/', views.search_results, name='search-results'),
]
