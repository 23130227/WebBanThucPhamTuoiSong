import torch
import torch.nn.functional as F
from underthesea import word_tokenize


def predict_comment(comment, model, tokenizer):
    comment_segmented = word_tokenize(comment, format="text")
    encoding = tokenizer(
        comment_segmented,
        truncation=True,
        padding='max_length',
        max_length=256,
        return_tensors='pt'
    )

    device = next(model.parameters()).device
    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)

    with torch.no_grad():
        # --- TASK 1: KIỂM TRA LIÊN QUAN (RELEVANT) ---
        logits_relevant = model(input_ids, attention_mask, task="relevant")
        pred_relevant = torch.argmax(logits_relevant, dim=1).item()

        sentiment_label = None
        sentiment_score = None  # Tạo biến hứng điểm số

        # Chỉ phân tích cảm xúc nếu comment liên quan
        if pred_relevant == 1:
            # --- TASK 2: PHÂN TÍCH CẢM XÚC (SENTIMENT) ---
            logits_sentiment = model(input_ids, attention_mask, task="sentiment")

            # === ĐOẠN QUAN TRỌNG ===
            # Dùng Softmax để đổi logits thành xác suất (0.0 -> 1.0)
            probs = F.softmax(logits_sentiment, dim=1)

            # Lấy xác suất của lớp 1 (Positive)
            # probs[0] là mẫu đầu tiên, [1] là class Positive
            sentiment_score = probs[0][1].item()

            # Lấy nhãn (0 hoặc 1) dựa trên xác suất cao nhất (giữ lại để dùng nếu cần)
            sentiment_label = torch.argmax(logits_sentiment, dim=1).item()

    return {
        'relevant': int(pred_relevant),
        'sentiment': sentiment_label,  # Vẫn trả về 0 hoặc 1
        'sentiment_score': sentiment_score  # <--- TRẢ THÊM CÁI NÀY (VD: 0.8754)
    }