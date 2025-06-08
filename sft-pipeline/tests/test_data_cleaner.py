import pandas as pd
import pytest
from sft_pipeline.services.data_cleaner import DataCleaner

def test_clean_text_removes_whitespace():
    df = pd.DataFrame({
        "query": ["   test   query   ", None],
        "doc": ["   test   doc   ", "valid doc"],
        "label": [1, 0]
    })
    cleaner = DataCleaner(verbose=False)
    cleaner.clean_text(df)
    assert df["query"].iloc[0] == "test query"
    assert df["doc"].iloc[0] == "test doc"
    assert not df.isnull().any().any()

def test_filter_binary_labels_removes_non_binary():
    df = pd.DataFrame({
        "query": ["q1", "q2", "q3"],
        "doc": ["d1", "d2", "d3"],
        "label": [1, 2, 0]
    })
    cleaner = DataCleaner(verbose=False)
    cleaner.filter_binary_labels(df)
    assert df.shape[0] == 2
    assert set(df["label"].unique()) == {0, 1}

def test_drop_duplicates_and_check_labels_removes_duplicates():
    df = pd.DataFrame({
        "query": ["q1", "q1", "q2"],
        "doc": ["d1", "d1", "d2"],
        "label": [1, 1, 0]
    })
    cleaner = DataCleaner(verbose=False)
    cleaner.drop_duplicates_and_check_labels(df)
    assert df.shape[0] == 2
