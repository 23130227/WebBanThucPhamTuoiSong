from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect

from cart.forms import CheckoutForm
from cart.models import Order
from products.models import Product


# # Create your views here.

def get_cart_data(request):
    cart = request.session.get('cart', {})
    subtotal = 0

    for item in cart.values():
        item['total'] = int(item['price']) * int(item['quantity'])
        subtotal += item['total']

    delivery = 0
    discount = 0
    total = subtotal + delivery - discount

    return {
        'cart': cart,
        'subtotal': subtotal,
        'delivery': delivery,
        'discount': discount,
        'total': total,
    }


def cart_view(request):
    context = get_cart_data(request)
    return render(request, 'cart/cart.html', context)


def is_normal_user(user):
    return user.is_authenticated and not user.is_staff and not user.is_superuser


@login_required
@user_passes_test(is_normal_user)
@transaction.atomic
def checkout_view(request):
    cart_data = get_cart_data(request)

    if not cart_data['cart']:
        messages.error(
            request,
            "Giỏ hàng của bạn hiện trống. Vui lòng thêm sản phẩm trước khi thanh toán."
        )
        return redirect('cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            order = Order.objects.create(
                user=request.user,
                full_name=data['full_name'],
                phone=data['phone'],
                city=data['city'],
                district=data['district'],
                ward=data['ward'],
                address=data['address'],
                note=data['note'],
                payment_method=data['payment_method'],
                subtotal=cart_data['subtotal'],
                delivery=cart_data['delivery'],
                discount=cart_data['discount'],
                total=cart_data['total'],
            )

            for pid, item in cart_data['cart'].items():
                order.items.create(
                    product_id=int(pid),
                    product_name=item['name'],
                    product_price=item['price'],
                    quantity=item['quantity'],
                    total=item['total'],
                )

            del request.session['cart']
            request.session.modified = True

            return redirect('order_success')

    else:
        form = CheckoutForm()

    context = {
        **cart_data,
        'form': form,
    }
    return render(request, 'cart/checkout.html', context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    cart = request.session.get('cart', {})
    pid = str(product.id)

    if pid in cart:
        cart[pid]['quantity'] += quantity
    else:
        cart[pid] = {
            'name': product.name,
            'price': float(product.get_discount_price()),
            'quantity': quantity,
            'image': product.image.url if product.image else ''
        }

    request.session['cart'] = cart
    request.session.modified = True

    return redirect(request.META.get('HTTP_REFERER', '/'))


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)

    if pid in cart:
        del cart[pid]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


def update_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        pid = str(product_id)

        if pid in cart:
            try:
                qty = int(request.POST.get('quantity', 1))
                if qty > 0:
                    cart[pid]['quantity'] = qty
                else:
                    del cart[pid]
            except ValueError:
                pass

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart')
