from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('ve-chung-toi/', views.about_view, name='about'),
    path('lien-he/', views.contact_view, name='contact'),
    path('yeu-thich/', views.wishlist_view, name='wishlist'),
]
