from django.urls import path
from . import views

urlpatterns = [
    path('submit-review/<int:product_id>/', views.submit_review, name='submit_review'),
    path("<slug:category_slug>/<slug:product_slug>/", views.product_single_view, name="product_single"),
    path('all/', views.shop_all_products_view, name='shop_all_products'),
    path('<slug:category_slug>/', views.shop_by_category_view, name='shop_by_category'),
    path('search-results/', views.search_results_view, name='search_results'),
    path('wishlist/toggle/<int:product_id>/', views.wishlist_toggle, name='wishlist_toggle'),

]
