from app.models import pipeline

def run_inference(system_msg: str,
                  user_msg: str,
                  temperature: float,
                  top_p: float,
                  max_tokens: int) -> str:
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ]

    outputs = pipeline(
        messages,
        max_new_tokens=max_tokens,
        temperature=temperature
    )

    return outputs[0]["generated_text"][-1]