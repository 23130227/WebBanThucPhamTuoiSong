import torch
import torch.nn as nn
from transformers import AutoModel

class PhoBERTMultiTask(nn.Module):
    def __init__(self, model_name="vinai/phobert-base", num_labels_relevant=2, num_labels_sentiment=2):
        super(PhoBERTMultiTask, self).__init__()
        self.phobert = AutoModel. from_pretrained(model_name)
        hidden_size = self.phobert.config.hidden_size
        self.classifier_relevant = nn.Linear(hidden_size, num_labels_relevant)
        self.classifier_sentiment = nn.Linear(hidden_size, num_labels_sentiment)
        self.dropout = nn.Dropout(0.1)

    def forward(self, input_ids, attention_mask, task="relevant"):
        outputs = self.phobert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.last_hidden_state[:, 0, :]
        pooled_output = self. dropout(pooled_output)
        if task == "relevant":
            logits = self.classifier_relevant(pooled_output)
        elif task == "sentiment":
            logits = self.classifier_sentiment(pooled_output)
        return logits