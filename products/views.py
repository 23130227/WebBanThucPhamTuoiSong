from django.contrib.messages import error, success
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Avg
from django.db.models.functions import Random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import *
from products.ai.api_client import analyze_comment_api, check_server_health


# from products.ai.load_model import load_model, load_tokenizer
# from products.ai.predict import predict_comment

#
# # loadmodel AI
# MODEL_PATH = 'ai_models/phobert_multitask_Relevant_Sentiment_V2.pth'
# model = load_model(MODEL_PATH)
# tokenizer = load_tokenizer()
#
#
# def analyze_comment(comment_text):
#     return predict_comment(comment_text, model, tokenizer)

def analyze_comment(comment_text):
    """
    Wrapper function để gọi API AI Server.
    Giữ nguyên tên hàm để không phải sửa nhiều code khác.
    """
    result = analyze_comment_api(comment_text)

    if result is None:
        # Fallback khi API không hoạt động
        print("⚠️ AI Server không phản hồi, sử dụng fallback")
        return {
            'relevant': 1,  # Mặc định cho qua
            'sentiment': 1,  # Mặc định positive
            'prob_sentiment': [0.5, 0.5],
            'sentiment_score': 0.5  # Trung lập
        }

    # Chuyển đổi format để tương thích với code cũ
    # Thêm sentiment_score từ prob_sentiment
    if result.get('prob_sentiment'):
        result['sentiment_score'] = result['prob_sentiment'][1]  # Xác suất positive
    else:
        result['sentiment_score'] = 0.5

    return result


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


def _get_wishlist_product_ids(request):
    if not request.user.is_authenticated:
        return set()
    return set(
        WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
    )


@require_POST
@login_required
@user_passes_test(is_normal_user)
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    obj, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    if created:
        success(request, "Đã thêm sản phẩm vào danh sách yêu thích.")
    else:
        obj.delete()
        success(request, "Đã xóa sản phẩm khỏi danh sách yêu thích.")

    return redirect(request.META.get('HTTP_REFERER', product.get_absolute_url()))


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

    wishlist_product_ids = _get_wishlist_product_ids(request)

    context = {'products': products, 'categories': categories, 'current_category': None,
               'wishlist_product_ids': wishlist_product_ids, }
    return render(request, 'products/shop.html', context)


def shop_by_category_view(request, category_slug):
    context = {}
    category = get_object_or_404(Category, slug=category_slug)
    product_list = Product.objects.active().filter(category=category).order_by('name')
    categories = Category.objects.all().order_by('name')
    paginator = Paginator(product_list, 16)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    wishlist_product_ids = _get_wishlist_product_ids(request)

    context = {
        'products': products,
        'categories': categories,
        'current_category': category,
        'wishlist_product_ids': wishlist_product_ids,
    }
    return render(request, 'products/shop.html', context)


def search_results_view(request):
    context = {}
    return render(request, 'products/search-results.html', context)


blackList = [  # Từ tục tĩu, chửi thề (tiếng Việt)
    "địt", "cứt", "lồn", "cặc", "buồi", "đéo", "đỉ", "đĩ", "vkl", "vcc", "clm", "clgt", "dm", "dcm", "đkm",
    "f*ck", "fuck", "shit", "asshole", "bitch", "motherfucker", "dildo", "xxx",
    # Phân biệt chủng tộc, nhạy cảm đến màu da/tôn giáo/giới tính
    "da đen", "mọi rợ", "phản động", "khủng bố", "dao động", "gay", "les", "pede", "bóng lộ", "bê đê",
    # Spam, quảng cáo
    "xxx", "sex", "loan tin", "cược", "cá độ", "đánh bạc", "lô đề", "mua bán dâm", "play game", "nhận thưởng",
    "chuẩn bị vào tù", "free fire", "quảng cáo", "link liên kết", "ib shop mình", "giá rẻ", "khuyến mãi", "cho tiền",
    "nhận quà",
    # Tấn công cá nhân hoặc miệt thị
    "ngu", "óc chó", "đần", "chó", "lừa đảo", "đồ khốn", "đồ ngu", "bại não",
    # Từ nhạy cảm tiếng Anh
    "porn", "nude", "nsfw", "blowjob", "cum", "anal", "dick", "pussy", "retard", "niga", "nigger"
]


def check_ban_review(text):
    text_lower = text.lower()
    for word in blackList:
        if word in text_lower:
            return True, word
    return False, None


@login_required
@user_passes_test(is_normal_user)
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        rating = request.POST.get('rating', 0)
        comment = request.POST.get('comment', '').strip()
        user = request.user

        if not OrderItem.objects.filter(order__user=user, product=product).exists():
            messages.error(request, f"Chỉ khách hàng đã mua sản phẩm mới được phép đánh giá!")
            return redirect(product.get_absolute_url())

        # Kiểm tra từ cấm
        isbad, word_bad = check_ban_review(comment)
        if isbad:
            print(f"Ban: Comment chứa từ cấm '{word_bad}'")
            messages.error(request, f"Bình luận của bạn chứa từ ngữ không phù hợp: '{word_bad}'")
            return redirect(product.get_absolute_url())

        # ========== GỌI API AI SERVER ==========
        ai_result = analyze_comment(comment)

        print("\n" + "=" * 60)
        print(f" Nội dung: {comment}")

        is_relevant = ai_result.get('relevant', 0)
        print(f" Chủ đề: {'✅ relevant' if is_relevant == 1 else '❌ irrelevant'}")

        if is_relevant == 1:
            score = ai_result.get('sentiment_score', 0.5)

            percent_pos = round(score * 100, 2)
            percent_neg = round((1 - score) * 100, 2)

            print(f" Sentiment Analysis:")
            print(f"   + positive: {percent_pos}%")
            print(f"   + negative: {percent_neg}%")

            sentiment_status = "positive" if score > 0.5 else "negative"
            print(f" Result AI: {sentiment_status}")

            review, created = Review.objects.get_or_create(
                product=product,
                user=user,
                defaults={'rating': rating, 'comment': comment,
                          'ai_positive_score': score,
                          'ai_negative_score': 1 - score,
                          'ai_sentiment': sentiment_status},
            )

            if created:
                success(request, "Cảm ơn bạn đã gửi đánh giá!")
            else:
                review.rating = rating
                review.comment = comment
                review.ai_positive_score = score
                review.ai_negative_score = 1 - score
                review.ai_sentiment = sentiment_status
                review.save()
                success(request, "Đánh giá của bạn đã được cập nhật!")

        print("=" * 60 + "\n")

        if is_relevant == 0:
            messages.error(request, "Nội dung bình luận không liên quan đến sản phẩm! Vui lòng nhập lại.")
            return redirect(product.get_absolute_url())

    return redirect(product.get_absolute_url())


@login_required
def wishlist_view(request):
    items = (
        WishlistItem.objects.filter(user=request.user)
        .select_related('product', 'product__category')
        .order_by('-created_at')
    )
    context = {'wishlist_items': items}
    return render(request, 'products/wishlist.html', context)
