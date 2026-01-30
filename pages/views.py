import time
from django.contrib.auth.decorators import login_required
import os
from django.http import JsonResponse
from django.shortcuts import render

from pages.models import HomeSlide
from products.models import Product, Review, WishlistItem
from django.views.decorators.csrf import csrf_exempt
from products.models import Product
from llama_cpp import Llama


TEN_FILE_MODEL = "Qwen2.5-7B-Instruct.Q4_K_M-002.gguf"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'ai_models', TEN_FILE_MODEL)

print(f"Đang nạp Model từ: {MODEL_PATH}")

try:
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_gpu_layers=0,
        verbose=False,
    )
    print("Model AI đã sẵn sàng!")
except Exception as e:
    print(f"LỖI LOAD MODEL: {e}")
    llm = None



@csrf_exempt
def ai_chat(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()

        if not user_message:
            return JsonResponse({'reply': 'Xin mời nhập nguyên liệu...'})

        if llm is None:
            return JsonResponse({'reply': 'Lỗi Server AI.'})

        system_content = (
            "Bạn là Bếp Trưởng AI độc quyền của Website FreshFood. "
            "Nhiệm vụ DUY NHẤT của bạn là tư vấn công thức nấu ăn dựa trên nguyên liệu thực tế. "

            "QUY TẮC XỬ LÝ ĐẦU VÀO (BẮT BUỘC TUÂN THỦ):"
            "1. KIỂM TRA NGUYÊN LIỆU: Chỉ chấp nhận các nguyên liệu là THỰC PHẨM, GIA VỊ hoặc DỤNG CỤ NẤU ĂN có thật và ăn được. "
            "   - Nếu người dùng nhập những thứ phi thực phẩm (ví dụ: 'gạch', 'xe máy', 'iphone', 'nỗi buồn'), nhập ký tự vô nghĩa (spam 'asdf', '1234'), hoặc các loại thịt/cá không có thật (ví dụ: 'thịt rồng', 'cá tiên'): Hãy từ chối và yêu cầu nhập lại nghiêm túc."

            "2. XỬ LÝ SỐ LƯỢNG THỊT/CÁ:"
            "   - Đếm số loại thịt hoặc cá trong danh sách nguyên liệu."
            "   - Nếu > 2 loại (ví dụ: vừa có gà, bò, lẫn cá hồi): Hãy trả lời: 'Xin lỗi, để món ăn ngon nhất, vui lòng chỉ chọn tối đa 1 loại thịt hoặc cá làm món chính thôi nhé!'."
            "   - Nếu 0 - 1 loại: Xử lý bình thường (gợi ý món chay nếu là 0, món mặn nếu là 1)."

            "3. PHẠM VI TRẢ LỜI:"
            "   - Tuyệt đối KHÔNG trả lời về du lịch, code, học tập, chính trị hay đời sống."
            "   - Nếu bị hỏi 'Bạn là ai?', trả lời đúng nguyên văn: 'Tôi là Bếp Trưởng AI, tôi chỉ biết nấu ăn thôi, bạn có nguyên liệu gì không?'"

            "4. PHONG CÁCH:"
            "   - Trả lời ngắn gọn, thân thiện, tập trung ngay vào tên món và cách làm sơ lược."
        )

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_message}
        ]

        try:
            output = llm.create_chat_completion(
                messages=messages,
                max_tokens=512,
                temperature=0.7,
                top_p=0.9,
            )

            ai_message = output['choices'][0]['message']['content'].strip()

            return JsonResponse({'reply': ai_message})

        except Exception as e:
            print(f"Lỗi: {e}")
            return JsonResponse({'reply': 'Đầu bếp đang bận, thử lại sau nhé!'})

    return JsonResponse({'error': 'Sai method'}, status=400)


def index_view(request):
    slides = HomeSlide.objects.filter(is_active=True)
    top_sold_products = Product.objects.active().order_by('-sold_quantity')[:8]
    products = list(Product.objects.active())
    products_with_discount = [p for p in products if p.get_discount_percentage_preview() > 0]
    product_max_discount = max(products_with_discount, key=lambda p: p.get_discount_percentage_preview(), default=None)
    top_reviews = Review.objects.filter(rating__gte=4).order_by('-created_at')[:5]

    wishlist_product_ids = set()
    if request.user.is_authenticated:
        wishlist_product_ids = set(
            WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True)
        )
    context = {'slides': slides, 'top_sold_products': top_sold_products, 'product_max_discount': product_max_discount,
               'top_reviews': top_reviews, 'wishlist_product_ids': wishlist_product_ids, }
    return render(request, 'pages/index.html', context)


def about_view(request):
    context = {}
    return render(request, 'pages/about.html', context)


def contact_view(request):
    context = {}
    return render(request, 'pages/contact.html', context)
