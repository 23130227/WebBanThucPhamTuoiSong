from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Avg
from django.db.models.functions import Random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ai_core.services import check_is_spam

from .models import *


# Create your views here.
def product_single_view(request, category_slug, product_slug):
    context = {}
    category = get_object_or_404(Category, slug=category_slug)
    product = get_object_or_404(Product, slug=product_slug, category=category)
    avg_rating = product.reviews.aggregate(
        avg=Avg('rating')
    )['avg'] or 0
    full_star = int(avg_rating) + (1 if avg_rating - int(avg_rating) >= 0.75 else 0)
    half_star = 1 if 0.25 <= avg_rating - int(avg_rating) < 0.75 else 0
    empty_star = 5 - full_star - half_star
    product.avg_rating = avg_rating
    product.full_star = range(full_star)
    product.half_star = half_star
    product.empty_star = range(empty_star)
    reviews = product.reviews.all().order_by(
        '-created_at')
    for r in reviews:
        r.stars = range(r.rating)
        r.empty_stars = range(5 - r.rating)
    related_products = (Product.objects.filter(category=category).exclude(pk=product.pk).order_by(Random())[:4])
    context = {'product': product, 'reviews': reviews, 'related_products': related_products}
    return render(request, "products/product-single.html", context)


def is_normal_user(user):
    return user.is_authenticated and not user.is_staff and not user.is_superuser


# @login_required
# @user_passes_test(is_normal_user)
# def submit_review(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     rating = request.POST.get('rating', 0)
#     user = request.user
#     comment = request.POST.get('comment', '').strip()
#     if request.method == 'POST':
#         review, created = Review.objects.get_or_create(
#             product=product,
#             user=user,
#             defaults={'rating': rating, 'comment': comment}
#         )
#         if created:
#             messages.success(request, "Cảm ơn bạn đã gửi đánh giá!")
#         else:
#             review.rating = rating
#             review.comment = comment
#             review.save()
#             messages.success(request, "Đánh giá của bạn đã được cập nhật!")
#     return redirect(product.get_absolute_url())


def shop_all_products_view(request):
    context = {}
    product_list = Product.objects.active().all().select_related('category').order_by('name')
    categories = Category.objects.all().order_by('name')

    paginator = Paginator(product_list, 16)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    context = {'products': products, 'categories': categories, 'current_category': None}
    return render(request, 'products/shop.html', context)


def shop_by_category_view(request, category_slug):
    context = {}
    category = get_object_or_404(Category, slug=category_slug)
    product_list = Product.objects.active().filter(category=category).order_by('name')
    categories = Category.objects.all().order_by('name')
    paginator = Paginator(product_list, 16)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    context = {'products': products, 'categories': categories, 'current_category': category}
    return render(request, 'products/shop.html', context)


def search_results_view(request):
    context = {}
    return render(request, 'products/search-results.html', context)


@login_required
@user_passes_test(is_normal_user)
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        rating = request.POST.get('rating', 0)
        comment = request.POST.get('comment', '').strip()
        user = request.user

        # === 🔴 CHÈN CODE AI VÀO ĐÂY ===
        if comment:
            # Gọi hàm kiểm tra
            if check_is_spam(comment):
                # Nếu là Spam: Báo lỗi đỏ và đuổi về, KHÔNG LƯU
                messages.error(request, "Bình luận bị chặn vì nghi vấn Spam/Quảng cáo!")
                return redirect(product.get_absolute_url())
        # === 🟢 HẾT CODE AI ===

        # (Code cũ của bạn giữ nguyên bên dưới)
        review, created = Review.objects.get_or_create(
            product=product,
            user=user,
            defaults={'rating': rating, 'comment': comment}
        )
        if created:
            messages.success(request, "Cảm ơn bạn đã gửi đánh giá!")
        else:
            review.rating = rating
            review.comment = comment
            review.save()
            messages.success(request, "Đánh giá của bạn đã được cập nhật!")

    return redirect(product.get_absolute_url())
