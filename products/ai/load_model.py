import torch
from transformers import AutoTokenizer
from .phobert_model import PhoBERTMultiTask

def load_model(model_path):
    model = PhoBERTMultiTask()
    model.load_state_dict(torch.load(model_path, map_location=torch. device('cpu')))
    model.eval()
    return model

def load_tokenizer():
    return AutoTokenizer.from_pretrained("vinai/phobert-base")