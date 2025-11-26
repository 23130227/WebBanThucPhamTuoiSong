from django.shortcuts import render


# Create your views here.
def product_single(request):
    context = {}
    return render(request, 'products/product-single.html', context)


def shop(request):
    context = {}
    return render(request, 'products/shop.html', context)


def search_results(request):
    context = {}
    return render(request, 'products/search-results.html', context)
