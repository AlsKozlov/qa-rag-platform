from typing import List
import re


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[■●◆▪►◄•♦✓✔➤→←⇨»«►▶]', '', text)
    text = re.sub(r'\.{3,}', '...', text)
    text = re.sub(r'-{2,}', '-', text)
    return text.strip()


def filter_chunks(chunks: List[str], min_chars: int = 100) -> List[str]:
    cleaned = []
    for chunk in chunks:
        text = re.sub(r'\s+', ' ', chunk).strip()
        letter_count = sum(c.isalpha() for c in text)
        if len(text) >= min_chars and letter_count / len(text) > 0.5:
            cleaned.append(text)
    return cleaned


def deduplicate_chunks(chunks: List[str]) -> List[str]:
    seen = set()
    unique = []
    for chunk in chunks:
        norm = chunk.strip().lower()
        if norm not in seen:
            seen.add(norm)
            unique.append(chunk)
    return unique


def has_capslock_block(text: str, min_len: int = 3, ratio: float = 0.5) -> bool:
    clean = re.sub(r'[^A-Za-zА-Яа-я0-9 ]', '', text)
    upper_count = sum(1 for c in clean if c.isupper())
    total = sum(1 for c in clean if c.isalpha())
    upper_runs = re.findall(r'[A-ZА-Я]{' + str(min_len) + r',}', clean)
    if upper_runs or (total > 0 and upper_count / total >= ratio):
        return True
    return False


def is_heading(paragraph) -> bool:
    text = paragraph.text.strip()
    if re.match(r'^(ГЛАВА|СТАТЬЯ)\s+\d+[\.\)]?', text.upper()):
        return True
    runs = paragraph.runs
    if runs and any(run.bold for run in runs):
        if has_capslock_block(text, min_len=3, ratio=0.5):
            return True
    if len(runs) == 1:
        run = runs[0]
        if run.bold and text.isupper() and len(text) > 5:
            return True
    return False


def split_by_sentences(text: str, max_len: int = 12000) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    buffer = ""
    for sentence in sentences:
        if len(buffer) + len(sentence) <= max_len:
            buffer += sentence + " "
        else:
            chunks.append(buffer.strip())
            buffer = sentence + " "
    if buffer:
        chunks.append(buffer.strip())
    return chunks