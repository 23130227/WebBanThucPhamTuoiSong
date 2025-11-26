from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('profile/', views.profile, name='profile'),
    path('password-change/', views.password_change, name='password-change'),
]
