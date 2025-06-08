import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sentence_transformers import SentenceTransformer

from services.data_cleaner import DataCleaner
from services.model_pipeline import SFTBiEncoderPipeline
import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
from typing import Dict, Union, List


def evaluate_similarity(preds: Union[List[float], np.ndarray],
                        targets: Union[List[float], np.ndarray],
                        verbose: bool = True) -> Dict[str, float]:
    preds = np.array(preds)
    targets = np.array(targets)
    rho, _ = spearmanr(preds, targets)
    rho = 0.0 if np.isnan(rho) else rho
    mse = np.mean((preds - targets) ** 2)
    auc = roc_auc_score(targets, preds)
    if verbose:
        print(f"Spearman: {rho:.4f}, AUC-ROC: {auc:.4f}, MSE: {mse:.4f}")
    return {"Spearman": rho, "AUC-ROC": auc, "MSE": mse}


def run_pipeline(local_data_path: str, model_save_path: str,
                 model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
    data = pd.read_csv(local_data_path)
    cleaner = DataCleaner()
    cleaner.basic_info(data)
    cleaner.clean_text(data)
    cleaner.filter_binary_labels(data)
    cleaner.drop_duplicates_and_check_labels(data)
    cleaner.visualize(data)

    train_df, temp_df = train_test_split(data, test_size=0.3, random_state=42, shuffle=True)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, shuffle=True)

    if os.path.exists(model_save_path) and os.listdir(model_save_path):
        base_model_name = model_save_path
    else:
        base_model_name = model_name

    pipeline = SFTBiEncoderPipeline(
        model_name=base_model_name,
        train_df=train_df,
        val_df=val_df,
        test_df=test_df,
        model_save_path=model_save_path
    )
    pipeline.prepare_examples()
    pipeline.prepare_model_with_lora()
    pipeline.create_evaluator()
    pipeline.run_optuna(n_trials=20)
    pipeline.train_final_model()

    sft_biencoder = SentenceTransformer(model_save_path)
    query_emb = sft_biencoder.encode(test_df["query"], normalize_embeddings=True)
    doc_emb = sft_biencoder.encode(test_df["doc"], normalize_embeddings=True)
    preds = (query_emb * doc_emb).sum(axis=1)
    metrics = evaluate_similarity(preds, test_df["label"].values)
    print("Final metrics:", metrics)
    return metrics
