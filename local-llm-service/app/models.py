from app.config import settings
import transformers
import torch
from huggingface_hub import login

login(settings.HF_TOKEN)

pipeline = transformers.pipeline(
    "text-generation",
    model=settings.MODEL_NAME,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)
