import pandas as pd
from dags.services.run_pipeline_service import run_pipeline

def test_run_pipeline_returns_metrics(tmp_path):
    df = pd.DataFrame({
        "query": ["q1", "q2"],
        "doc": ["d1", "d2"],
        "label": [1, 0]
    })
    test_csv = tmp_path / "data.csv"
    df.to_csv(test_csv, index=False)
    metrics = run_pipeline(str(test_csv), "./model")
    assert "Spearman" in metrics
    assert "AUC-ROC" in metrics
    assert "MSE" in metrics
