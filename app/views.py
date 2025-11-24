from django.shortcuts import render


# Create your views here.

def home(request):
    context = {}
    return render(request, 'app/home.html', context)


def cart(request):
    context = {}
    return render(request, 'app/cart.html', context)
