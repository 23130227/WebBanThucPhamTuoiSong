from django.shortcuts import render

from products.models import Product


# Create your views here.

def index(request):
    context = {'products': Product.objects.all().select_related('category').order_by('name')}
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
