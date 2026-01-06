from django.urls import path
from . import views

urlpatterns = [
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path('', views.index_view, name='index'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
]
