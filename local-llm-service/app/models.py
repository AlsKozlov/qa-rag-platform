from transformers import AutoTokenizer, AutoModelForCausalLM
from app.config import settings
#from vllm import LLM
import transformers
import torch
from huggingface_hub import login

login(settings.HF_TOKEN)

# tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_NAME, use_auth_token=True)
# model = AutoModelForCausalLM.from_pretrained(settings.MODEL_NAME, use_auth_token=True)

pipeline = transformers.pipeline(
    "text-generation",
    model=settings.MODEL_NAME,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)
# llm = LLM(model=settings.MODEL_NAME)
