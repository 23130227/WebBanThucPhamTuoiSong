import os

import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from pages.models import HomeSlide
from products.models import Product, Review, WishlistItem


# BASE_DIR chỉ cần khi bạn có nhu cầu đặc biệt về file, ở đây có thể bỏ qua nếu không dùng.

@csrf_exempt
def ai_chat(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if not user_message:
            return JsonResponse({'reply': 'Xin mời nhập nguyên liệu...'})

        system_instruction = (
            "Bạn là Chuyên gia Ẩm thực khó tính của FreshFood. Nguyên tắc cốt lõi: CHỈ tư vấn món ăn CHUẨN MỰC, HOÀN CHỈNH."
            "\n\n"
            "QUY TẮC XỬ LÝ NGUYÊN LIỆU (QUAN TRỌNG):"
            "1. KIỂM TRA ĐỦ: Nếu người dùng đưa nguyên liệu sơ sài (ví dụ: chỉ có Bánh mì + Chuối), hãy kiểm tra xem có đủ để làm một món danh tiếng không (VD: Bánh Chuối Nướng cần cốt dừa, đường; Chuối chiên cần bột). "
            "   -> NẾU KHÔNG ĐỦ để tạo thành món ngon chuẩn vị: Hãy từ chối khéo và gợi ý nguyên liệu còn thiếu. TUYỆT ĐỐI KHÔNG tự bịa ra cách làm sơ sài kiểu 'nướng lên ăn kèm' hay 'luộc lên chấm muối' để đối phó."
            "2. KHÔNG CHẤP NHẬN MÓN 'CHỮA CHÁY': Không đưa ra các món ăn vặt tự chế, các món ghép tên mô tả (như 'Cơm trộn nước lọc', 'Bánh mì kẹp táo'). Chỉ đưa ra món có tên riêng trong từ điển ẩm thực (như 'Phở', 'Bò Lúc Lắc', 'Sandwich Chuối Nướng kiểu Pháp')."
            "\n\n"
            "KỊCH BẢN TRẢ LỜI:"
            "- Trường hợp 1 (Nguyên liệu rác/phi thực phẩm/quá tạp nham):"
            "  Trả lời: 'Xin lỗi, nguyên liệu bạn cung cấp không hợp lệ hoặc không thể kết hợp an toàn trong ẩm thực.'"
            "- Trường hợp 2 (Nguyên liệu hợp lệ nhưng quá ít/thiếu gia vị chính):"
            "  Ví dụ khách đưa 'Bánh mì, Chuối'. Đừng bịa món. "
            "  Trả lời: 'Với Bánh mì và Chuối, bạn đang thiếu các nguyên liệu kết dính như Sữa, Trứng hoặc Nước cốt dừa để làm các món ngon như Bánh Chuối Nướng hay French Toast. Bạn có muốn nhập thêm nguyên liệu không?'"
            "- Trường hợp 3 (Đủ nguyên liệu làm món ngon):"
            "  Trả lời theo format HTML sau (Không dùng Markdown):"
            "  <b>Tên Món Ăn</b> (Nêu rõ xuất xứ/đặc trưng)"
            "  <br><i>Lưu ý: Công thức chuẩn vị cần có thêm gia vị cơ bản.</i>"
            "  <br><b>Nguyên liệu cần thiết:</b> <ul><li>...</li></ul>"
            "  <b>Cách thực hiện:</b> <ol><li>...</li></ol>"
            "  <b>Yêu cầu thành phẩm:</b> Mô tả màu sắc, hương vị chuẩn."
            "\n\n"
            "HÃY NHỚ: Thà từ chối tư vấn vì thiếu nguyên liệu còn hơn đưa ra một công thức dở tệ hoặc tự chế."
        )

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer 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",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8000",  # bắt buộc với OpenRouter
                    "X-Title": "FreshFood AI Chef"
                },
                json={
                    "model": "google/gemini-2.0-flash-001",  # 👉 đổi model tại đây
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.5,
                },
                timeout=60
            )

            if response.status_code != 200:
                print("OpenRouter Error:", response.text)
                raise Exception(response.text)

            data = response.json()

            if "choices" not in data:
                raise Exception(data)

            reply = data["choices"][0]["message"]["content"]
            return JsonResponse({'reply': reply})

        except Exception as e:
            print("AI ERROR:", e)
            return JsonResponse({'reply': 'Đầu bếp đang bận, thử lại sau nhé!'})

    return JsonResponse({'error': 'Sai method'}, status=400)


# Trang chủ & các trang cơ bản khác giữ nguyên
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
    context = {
        'slides': slides,
        'top_sold_products': top_sold_products,
        'product_max_discount': product_max_discount,
        'top_reviews': top_reviews,
        'wishlist_product_ids': wishlist_product_ids
    }
    return render(request, 'pages/index.html', context)


def about_view(request):
    return render(request, 'pages/about.html', {})


def contact_view(request):
    return render(request, 'pages/contact.html', {})
