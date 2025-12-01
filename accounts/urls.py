from django.urls import path
from . import views

urlpatterns = [
    path('dang-ky/', views.register, name='register'),
    path('dang-nhap/', views.login, name='login'),
    path('quen-mat-khau/', views.forgot_password, name='forgot-password'),
    path('thong-tin-ca-nhan/', views.profile, name='profile'),
    path('doi-mat-khau/', views.password_change, name='password-change'),
]
