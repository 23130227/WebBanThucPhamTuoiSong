from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Order


@login_required
def order_history_view(request):
    qs = (
        Order.objects
        .filter(user=request.user)
        .order_by('-created_at', '-id')
    )

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'orders': page_obj.object_list,
    }
    return render(request, 'orders/order-history.html', context)


@login_required
def order_single_view(request, order_id: int):
    order = get_object_or_404(
        Order.objects.prefetch_related('items', 'items__product'),
        id=order_id,
        user=request.user,
    )

    context = {
        'order': order,
        'items': order.items.all(),
    }
    return render(request, 'orders/order-single.html', context)


@login_required
def order_success_view(request):
    context = {}
    return render(request, 'orders/order-success.html', context)
