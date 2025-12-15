from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from products.models import Product


# # Create your views here.


def cart_view(request):
    cart = request.session.get('cart', {})

    subtotal = 0
    for item in cart.values():
        item['total'] = int(item['price']) * int(item['quantity'])
        subtotal += item['total']

    return render(request, 'cart/cart.html', {
        'cart': cart,
        'subtotal': subtotal,
        'total': subtotal
    })


@login_required
def checkout_view(request):
    cart = request.session.get('cart')
    if not cart:
        messages.error(
            request,
            "Giỏ hàng của bạn hiện trống. Vui lòng thêm sản phẩm trước khi thanh toán."
        )
        return redirect('cart')
    subtotal = 0
    for item in cart.values():
        item['total'] = int(item['price']) * int(item['quantity'])
        subtotal += item['total']
    return render(request, 'cart/checkout.html', {'cart': cart, 'subtotal': subtotal, 'total': subtotal})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})
    pid = str(product.id)

    if pid in cart:
        cart[pid]['quantity'] += 1
    else:
        cart[pid] = {
            'name': product.name,
            'price': float(product.get_discount_price()),
            'quantity': 1,
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
