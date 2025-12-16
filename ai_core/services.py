import re
import torch
from transformers import pipeline
from langdetect import detect, LangDetectException

# --- CẤU HÌNH ---
device = 0 if torch.cuda.is_available() else -1
print(f"🚀 AI Zero-Shot đang khởi động trên: {'GPU' if device == 0 else 'CPU'}")

# --- LOAD MODEL ĐA NĂNG (ZERO-SHOT) ---
try:
    # Model này cho phép tự định nghĩa nhãn (Labels)
    spam_classifier = pipeline(
        "zero-shot-classification",
        model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
        device=device
    )
    print("✅ Đã tải Model Zero-Shot thành công!")
except Exception as e:
    print(f"❌ Lỗi tải Model: {e}")
    spam_classifier = None

def is_vietnamese_or_english(text):
    """Kiểm tra nếu là tiếng Việt hoặc tiếng Anh."""
    try:
        lang = detect(text)
        return lang in ['vi', 'en']
    except LangDetectException:
        return False

def looks_like_gibberish(text):
    """Chặn comment dạng toàn ký tự ngẫu nhiên không có từ thật."""
    total_alpha = len(re.findall(r'[a-zA-Z]', text))
    total_len = len(text)
    if total_len == 0:
        return True
    ratio = total_alpha / total_len
    # Nếu tỷ lệ ký tự alphabet quá cao nhưng lại không có nguyên âm → nghi gibberish
    return (ratio > 0.8 and not any(char in "aeiouy" for char in text.lower()))

def check_is_spam(text):
    print("\n" + "=" * 30)
    print(f"🔍 ĐANG KIỂM TRA: '{text}'")

    # 1. Check gibberish (chuỗi vô nghĩa, random ký tự)
    if looks_like_gibberish(text):
        print("🚫 KẾT LUẬN: CHẶN (chuỗi vô nghĩa/gibberish)")
        return True

    # 2. Check English/Vietnamese
    if not is_vietnamese_or_english(text):
        print("🚫 KẾT LUẬN: CHẶN (không phải tiếng Việt hoặc tiếng Anh)")
        return True

    # 3. Check spam AI
    if not spam_classifier:
        print("⚠️ Model chưa sẵn sàng -> Cho qua")
        return False

    try:
        candidate_labels = [
            "quảng cáo bán hàng",
            "lừa đảo",
            "cờ bạc",
            "bình luận sản phẩm bình thường"
        ]
        result = spam_classifier(text, candidate_labels, multi_label=False)
        top_label = result['labels'][0]
        top_score = result['scores'][0]
        print(f"👉 AI PHÁN ĐOÁN: Là '{top_label}' (Độ tin cậy: {top_score:.2f})")

        if top_label == "bình luận sản phẩm bình thường":
            print("✅ KẾT LUẬN: SẠCH")
            print("=" * 30 + "\n")
            return False

        if top_score > 0.4:
            print(f"🚫 KẾT LUẬN: CHẶN (Phát hiện: {top_label})")
            print("=" * 30 + "\n")
            return True
        else:
            print(f"⚠️ NGHI NGỜ: {top_label} nhưng điểm thấp ({top_score:.2f}) -> Tạm tha")
            return False

    except Exception as e:
        print(f"❌ LỖI KHI XỬ LÝ AI: {e}")
        return False