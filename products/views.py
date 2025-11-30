from django.shortcuts import render, get_object_or_404
from .models import *


# Create your views here.
def product_single(request, category_slug, product_slug):
    category = get_object_or_404(Category, slug=category_slug)
    product = get_object_or_404(Product, slug=product_slug, category=category)
    return render(request, "products/product-single.html",
                  {"product": product, "category": category})


def shop(request):
    context = {}
    return render(request, 'products/shop.html', context)


def search_results(request):
    context = {}
    return render(request, 'products/search-results.html', context)
