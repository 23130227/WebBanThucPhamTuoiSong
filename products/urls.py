from django.urls import path
from . import views

urlpatterns = [
    path('submit-review/<int:product_id>/', views.submit_review, name='submit-review'),
    path("<slug:category_slug>/<slug:product_slug>/", views.product_single_view, name="product-single"),
    path('tat-ca-san-pham/', views.shop_all_products_view, name='shop-all-products'),
    path('<slug:category_slug>/', views.shop_by_category_view, name='shop-by-category'),
    path('tim-kiem/', views.search_results_view, name='search-results'),
]
