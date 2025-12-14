from django.urls import path
from . import views

urlpatterns = [
    path('dang-ky/', views.register_view, name='register'),
    path('dang-nhap/', views.login_view, name='login'),
    path('dang-xuat/', views.logout_view, name='logout'),
    path('quen-mat-khau/', views.forgot_password_view, name='forgot-password'),
    path('thong-tin-ca-nhan/', views.profile_view, name='profile'),
    path('doi-mat-khau/', views.password_change_view, name='password-change'),
]
