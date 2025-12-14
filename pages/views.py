from django.shortcuts import render

from products.models import Product


# Create your views here.

def index(request):
    top_sold_products = Product.objects.active().order_by('-sold_quantity')[:8]
    context = {'top_sold_products': top_sold_products}
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

