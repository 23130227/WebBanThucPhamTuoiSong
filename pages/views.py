import time

from django.http import JsonResponse
from django.shortcuts import render

from pages.models import HomeSlide
from products.models import Product


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
    context = {'slides': slides, 'top_sold_products': top_sold_products}
    return render(request, 'pages/index.html', context)


def about_view(request):
    context = {}
    return render(request, 'pages/about.html', context)


def contact_view(request):
    context = {}
    return render(request, 'pages/contact.html', context)


def wishlist_view(request):
    context = {}
    return render(request, 'pages/wishlist.html', context)
