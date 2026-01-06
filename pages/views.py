import time
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from pages.models import HomeSlide
from products.models import Product, Review, WishlistItem


# Create your views here.

def ai_chat(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        ai_message = f'Bạn vừa nói: {user_message}'
        return JsonResponse({'reply': ai_message})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def index_view(request):
    slides = HomeSlide.objects.filter(is_active=True)
    top_sold_products = Product.objects.active().order_by('-sold_quantity')[:8]
    products = list(Product.objects.active())
    products_with_discount = [p for p in products if p.get_discount_percentage_preview() > 0]
    product_max_discount = max(products_with_discount, key=lambda p: p.get_discount_percentage_preview(), default=None)
    top_reviews = Review.objects.filter(rating__gte=4).order_by('-created_at')[:5]

    wishlist_product_ids = set()
    if request.user.is_authenticated:
        wishlist_product_ids = set(
            WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        )
    context = {'slides': slides,'top_sold_products': top_sold_products,'product_max_discount': product_max_discount,
               'top_reviews': top_reviews,'wishlist_product_ids': wishlist_product_ids,}
    return render(request, 'pages/index.html', context)


def about_view(request):
    context = {}
    return render(request, 'pages/about.html', context)


def contact_view(request):
    context = {}
    return render(request, 'pages/contact.html', context)


@login_required
def wishlist_view(request):
    items = (
        WishlistItem.objects.filter(user=request.user)
        .select_related('product', 'product__category')
        .order_by('-created_at')
    )
    context = {'wishlist_items': items}
    return render(request, 'pages/wishlist.html', context)
