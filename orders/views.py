from django.shortcuts import render


# Create your views here.
def order_history_view(request):
    context = {}
    return render(request, 'orders/order-history.html', context)


def order_detail_view(request):
    context = {}
    return render(request, 'orders/order-detail.html', context)


def order_success_view(request):
    context = {}
    return render(request, 'orders/order-success.html', context)
