from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg
from django.db.models.functions import Random
from django.shortcuts import render, get_object_or_404
from .models import *


# Create your views here.
def product_single_view(request, category_slug, product_slug):
    category = get_object_or_404(Category, slug=category_slug)
    product = get_object_or_404(Product, slug=product_slug, category=category)
    avg_rating = product.reviews.aggregate(
        avg=Avg('rating')
    )['avg'] or 0
    full_star = int(avg_rating) + (1 if avg_rating - int(avg_rating) >= 0.75 else 0)
    half_star = 1 if 0.25 <= avg_rating - int(avg_rating) < 0.75 else 0
    empty_star = 5 - full_star - half_star
    related_products = (Product.objects.filter(category=category).exclude(pk=product.pk).order_by(Random())[:4])
    return render(request, "products/product-single.html",
                  {'product': product, 'avg_rating': avg_rating, 'full_star': range(full_star), 'half_star': half_star,
                   'empty_star': range(empty_star),
                   'related_products': related_products})


@login_required
def submit_review(request, product_id):
    pass


def shop_all_products_view(request):
    product_list = Product.objects.all().select_related('category').order_by('name')
    categories = Category.objects.all().order_by('name')

    paginator = Paginator(product_list, 16)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, 'products/shop.html', {
        'products': products,
        'categories': categories,
        'current_category': None
    })


def shop_by_category_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    product_list = Product.objects.filter(category=category).order_by('name')
    categories = Category.objects.all().order_by('name')
    paginator = Paginator(product_list, 16)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    return render(request, 'products/shop.html',
                  {'products': products, 'categories': categories, 'current_category': category})


def search_results_view(request):
    context = {}
    return render(request, 'products/search-results.html', context)
