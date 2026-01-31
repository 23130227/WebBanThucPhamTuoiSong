from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_view, name='blog'),
    path('search/', views.blog_search_view, name='blog_search'),
    path('<int:post_id>/', views.blog_single_view, name='blog_single'),
]
