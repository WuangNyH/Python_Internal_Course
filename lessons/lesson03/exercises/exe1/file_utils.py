from typing import Dict


def read_file_content(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    return content


def normalize_text(text: str) -> str:
    text = text.lower()
    punctuations = ".,;:?!()[]\"'“”‘’"
    for ch in punctuations:
        text = text.replace(ch, " ")
    return text


def count_word_frequency(text: str) -> Dict[str, int]:
    normalized = normalize_text(text)
    words = normalized.split()

    freq: Dict[str, int] = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return freq
