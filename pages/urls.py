from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ve-chung-toi/', views.about, name='about'),
    path('lien-he/', views.contact, name='contact'),
    path('yeu-thich/', views.wishlist, name='wishlist'),
]
