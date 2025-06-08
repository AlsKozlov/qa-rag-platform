import os
import pandas as pd
from sft_pipeline.services.model_pipeline import SFTBiEncoderPipeline

def test_pipeline_prepares_examples():
    df = pd.DataFrame({"query": ["q1"], "doc": ["d1"], "label": [1]})
    pipeline = SFTBiEncoderPipeline("distilbert-base-uncased", df, df, df)
    pipeline.prepare_examples()
    assert len(pipeline.train_examples) == 1

def test_pipeline_uses_existing_model(monkeypatch):
    os.makedirs("./model", exist_ok=True)
    with open("./model/README.md", "w") as f:
        f.write("test")
    df = pd.DataFrame({"query": ["q1"], "doc": ["d1"], "label": [1]})
    pipeline = SFTBiEncoderPipeline("./model", df, df, df)
    pipeline.prepare_model_with_lora()
    assert pipeline.model is not None
