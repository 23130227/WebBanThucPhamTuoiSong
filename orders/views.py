from django.shortcuts import render


# Create your views here.
def order_history(request):
    context = {}
    return render(request, 'orders/order-history.html', context)


def order_detail(request):
    context = {}
    return render(request, 'orders/order-detail.html', context)


def order_success(request):
    context = {}
    return render(request, 'orders/order-success.html', context)
