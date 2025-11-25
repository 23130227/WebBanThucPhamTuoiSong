from django.shortcuts import render


# Create your views here.

def index(request):
    context = {}
    return render(request, 'app/index.html', context)


def product_single(request):
    context = {}
    return render(request, 'app/product-single.html', context)


def about(request):
    context = {}
    return render(request, 'app/about.html', context)


def blog(request):
    context = {}
    return render(request, 'app/blog.html', context)


def blog_single(request):
    context = {}
    return render(request, 'app/blog-single.html', context)


def cart(request):
    context = {}
    return render(request, 'app/cart.html', context)


def checkout(request):
    context = {}
    return render(request, 'app/checkout.html', context)


def contact(request):
    context = {}
    return render(request, 'app/contact.html', context)


def shop(request):
    context = {}
    return render(request, 'app/shop.html', context)


def wishlist(request):
    context = {}
    return render(request, 'app/wishlist.html', context)
