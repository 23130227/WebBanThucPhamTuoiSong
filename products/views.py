from django.db.models.functions import Random
from django.shortcuts import render, get_object_or_404
from .models import *


# Create your views here.
def product_single(request, category_slug, product_slug):
    category = get_object_or_404(Category, slug=category_slug)
    product = get_object_or_404(Product, slug=product_slug, category=category)
    related_products = (Product.objects.filter(category=category).exclude(pk=product.pk).order_by(Random())[:4])
    return render(request, "products/product-single.html",
                  {"product": product, "category": category, "related_products": related_products})


def shop_all_products(request):
    products = Product.objects.all().select_related('category').order_by('name')
    categories = Category.objects.all().order_by('name')
    return render(request, 'products/shop.html',
                  {'products': products, 'categories': categories, 'current_category': None})


def shop_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category).order_by('name')
    categories = Category.objects.all().order_by('name')
    return render(request, 'products/shop.html',
                  {'products': products, 'categories': categories, 'current_category': category})


def search_results(request):
    context = {}
    return render(request, 'products/search-results.html', context)
