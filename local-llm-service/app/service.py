from app.models import llm
from app.models import pipeline
# from vllm import SamplingParams

def run_inference(system_msg: str,
                  user_msg: str,
                  temperature: float,
                  top_p: float,
                  max_tokens: int) -> str:
    
    # prompt = f"<|SYSTEM|>: {system_msg}. <|USER|>: {user_msg}"

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ]

    # sampling_params = SamplingParams(
    #     max_tokens=max_tokens,
    #     temperature=temperature,
    #     top_p=top_p
    # )
    
    # outputs = llm.generate(prompt, sampling_params)

    outputs = pipeline(
        messages,
        max_new_tokens=max_tokens,
        temperature=temperature
    )

    return outputs[0]["generated_text"][-1]