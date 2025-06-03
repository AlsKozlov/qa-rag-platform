from sentence_transformers import SentenceTransformer
from sentence_transformers.models import Pooling, Transformer
from app.config import settings

def get_bi_encoder():

    raw_model = Transformer(model_name_or_path=settings.MODEL_NAME)

    bi_encoder_dim = raw_model.get_word_embedding_dimension()
    
    pooling_model = Pooling(
        bi_encoder_dim,
        pooling_mode_cls_token = False,
        pooling_mode_mean_tokens = True
    )

    bi_encoder = SentenceTransformer(
        modules = [raw_model, pooling_model],
        device = 'cpu'
    )
    
    return bi_encoder, bi_encoder_dim

BI_ENCODER, BI_ENCODER_DIM = get_bi_encoder()
