import pytest
import torch
from app.config import settings
from sentence_transformers import SentenceTransformer
from app.service import encode_process

@pytest.fixture(scope="session")
def bi_encoder():
    return SentenceTransformer(settings.MODEL_NAME)  

def test_encode_process_real_model(bi_encoder):
    text = "This is a test sentence."
    result = encode_process(bi_encoder, text)
    assert isinstance(result, torch.Tensor)
    assert result.shape[0] > 0

def test_encode_process_real_model_empty(bi_encoder):
    text = ""
    result = encode_process(bi_encoder, text)
    assert isinstance(result, torch.Tensor)
    assert result.shape[0] >= 0  