from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog, name='blog'),
    path('chi-tiet-blog/', views.blog_single, name='blog-single'),
]
