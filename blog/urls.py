from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_view, name='blog'),
    path('blog-single/', views.blog_single_view, name='blog_single'),
]
