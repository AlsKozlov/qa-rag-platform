import pytest
from etl.dags.services.base_service import (
    clean_text, filter_chunks, deduplicate_chunks, split_by_sentences
)

def test_clean_text_removes_extra_spaces():
    raw_text = "Test    text  with   multiple    spaces."
    cleaned = clean_text(raw_text)
    assert cleaned == "Test text with multiple spaces."

def test_filter_chunks_removes_short_chunks():
    chunks = ["short", "This is a valid chunk with enough content."]
    filtered = filter_chunks(chunks, min_chars=20)
    assert len(filtered) == 1
    assert filtered[0] == "This is a valid chunk with enough content."

def test_deduplicate_chunks_removes_duplicates():
    chunks = ["Chunk one.", "Chunk two.", "chunk one."]
    unique = deduplicate_chunks(chunks)
    assert len(unique) == 2

def test_split_by_sentences():
    text = "Sentence one. Sentence two! Sentence three?"
    chunks = split_by_sentences(text, max_len=50)
    assert all("." in chunk or "!" in chunk or "?" in chunk for chunk in chunks)
