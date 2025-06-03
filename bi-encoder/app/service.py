from sentence_transformers import SentenceTransformer
from typing import List, Union
from torch import Tensor
from numpy import ndarray

def encode_process(bi_encoder: SentenceTransformer, text: str) -> Union[List[Tensor], ndarray, Tensor]:

    embeddings = bi_encoder.encode(
        text,
        convert_to_tensor = True,
        show_progress_bar = False
    )

    return embeddings
    