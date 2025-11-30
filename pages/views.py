from django.shortcuts import render

from products.models import Product
from .models import *


# Create your views here.

def index(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'pages/index.html', context)


def about(request):
    context = {}
    return render(request, 'pages/about.html', context)


def contact(request):
    context = {}
    return render(request, 'pages/contact.html', context)


def wishlist(request):
    context = {}
    return render(request, 'pages/wishlist.html', context)
