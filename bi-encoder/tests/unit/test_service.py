import pytest
from app.service import encode_process
import torch
from sentence_transformers import SentenceTransformer


class DummyEncoder(SentenceTransformer):
    def encode(self, text, convert_to_tensor=True, show_progress_bar=False):
        if convert_to_tensor:
            return torch.tensor([0.1, 0.2, 0.3])
        else:
            return [0.1, 0.2, 0.3]


def test_encode_process_with_dummy(dummy_encoder=None):
    dummy_encoder = DummyEncoder()
    result = encode_process(dummy_encoder, "test")
    assert isinstance(result, list) or hasattr(result, 'shape')


def test_encode_process_empty_text_with_dummy(dummy_encoder=None):
    dummy_encoder = DummyEncoder()
    result = encode_process(dummy_encoder, "")
    assert isinstance(result, list) or hasattr(result, 'shape')