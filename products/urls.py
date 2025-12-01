from django.urls import path
from . import views

urlpatterns = [
    path("<slug:category_slug>/<slug:product_slug>/", views.product_single, name="product-single"),
    path('all-products/', views.shop, name='shop'),
    path('<slug:category_slug>/', views.shop_by_category, name='shop-by-category'),
    path('search-results/', views.search_results, name='search-results'),
]
