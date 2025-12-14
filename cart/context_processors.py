def cart_counter(request):
    cart = request.session.get('cart', {})
    return {
        'cart_count': sum(item.get('quantity', 0) for item in cart.values())
    }
