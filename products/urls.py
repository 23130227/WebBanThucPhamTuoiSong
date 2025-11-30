from django.urls import path
from . import views

urlpatterns = [
    path("<slug:category_slug>/<slug:product_slug>/", views.product_single, name="product-single"),
    path('shop/', views.shop, name='shop'),
    path('search-results/', views.search_results, name='search-results'),
]
