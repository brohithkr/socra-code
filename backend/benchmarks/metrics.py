from __future__ import annotations

import re
import numpy as np

from .embeddings import EmbeddingModel


WORD_RE = re.compile(r"[a-zA-Z_]+")


def token_f1(a: str, b: str) -> float:
    ta = set(WORD_RE.findall(a.lower()))
    tb = set(WORD_RE.findall(b.lower()))
    if not ta or not tb:
        return 0.0
    precision = len(ta & tb) / len(ta)
    recall = len(ta & tb) / len(tb)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    if vec_a.ndim == 1:
        vec_a = vec_a.reshape(1, -1)
    if vec_b.ndim == 1:
        vec_b = vec_b.reshape(1, -1)
    return float(np.dot(vec_a, vec_b.T).squeeze())


def socratic_compliance(text: str) -> float:
    score = 0.0
    if "?" in text:
        score += 0.5
    if "```" in text:
        score -= 0.2
    if any(word in text.lower() for word in ["here's", "solution", "fix", "replace"]):
        score -= 0.2
    return max(0.0, min(1.0, score))


def contains_code(text: str) -> bool:
    if "```" in text:
        return True
    if re.search(r"\bclass\b|\bdef\b|\b#include\b|\bpublic static\b", text):
        return True
    return False


def embed_similarity(embedder: EmbeddingModel, a: str, b: str) -> float:
    vecs = embedder.encode([a, b])
    return cosine_similarity(vecs[0], vecs[1])
