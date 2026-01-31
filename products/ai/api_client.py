import requests
from django.conf import settings

# URL của server AI trên Colab (cập nhật mỗi khi chạy lại Colab)
# Nên lưu trong settings.py hoặc biến môi trường
AI_SERVER_URL = "https://unfoisted-asuncion-nonrelativistic.ngrok-free.dev/"


def analyze_comment_api(comment_text, timeout=30):
    """
    Gọi API server AI trên Colab để phân tích comment.

    Args:
        comment_text: Nội dung comment cần phân tích
        timeout: Thời gian chờ tối đa (giây)

    Returns:
        dict: Kết quả phân tích từ AI
        {
            'relevant': 0 hoặc 1,
            'prob_relevant': [prob_0, prob_1],
            'sentiment': 0, 1 hoặc None,
            'prob_sentiment': [prob_0, prob_1] hoặc None
        }
    """
    try:
        response = requests.post(
            f"{AI_SERVER_URL}/predict",
            json={"comment": comment_text},
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API Error: Status {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print(f"❌ API Timeout sau {timeout}s")
        return None
    except requests.exceptions.ConnectionError:
        print(f"❌ Không thể kết nối đến AI Server: {AI_SERVER_URL}")
        return None
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
        return None


def check_server_health():
    """Kiểm tra server AI có hoạt động không"""
    try:
        response = requests.get(f"{AI_SERVER_URL}/health", timeout=10)
        return response.status_code == 200
    except:
        return False