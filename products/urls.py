from django.urls import path
from . import views

urlpatterns = [
    path("<slug:category_slug>/<slug:product_slug>/", views.product_single, name="product-single"),
    path('tat-ca-san-pham/', views.shop_all_products, name='shop-all-products'),
    path('<slug:category_slug>/', views.shop_by_category, name='shop-by-category'),
    path('tim-kiem/', views.search_results, name='search-results'),
]
