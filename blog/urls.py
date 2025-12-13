from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_view, name='blog'),
    path('chi-tiet-blog/', views.blog_single_view, name='blog-single'),
]
