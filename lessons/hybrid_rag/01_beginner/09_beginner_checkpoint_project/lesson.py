"""
Lesson 9: Beginner Checkpoint - Hybrid Search CLI.

No new concepts, this combines Lessons 1-8 into one small script.
Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/01_beginner/09_beginner_checkpoint_project/lesson.py
"""

import math
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"
EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
K1 = 1.5
B = 0.75
RRF_K = 60

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
    assert response.embeddings is not None
    result = []
    for embedding in response.embeddings:
        assert embedding.values is not None
        result.append(embedding.values)
    return result


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    return dot_product / (magnitude_a * magnitude_b)


def idf(term: str, documents: list[list[str]]) -> float:
    n = len(documents)
    doc_count = sum(1 for doc in documents if term in doc)
    return math.log((n - doc_count + 0.5) / (doc_count + 0.5) + 1)


def build_store(notes_dir: Path) -> dict:
    paths = sorted(notes_dir.glob("*.md"))
    names = [path.name for path in paths]
    texts = [path.read_text() for path in paths]
    return {
        "names": names,
        "texts": texts,
        "token_lists": [tokenize(text) for text in texts],
        "doc_vectors": embed_texts(texts),
    }


def dense_ranking(query_vector: list[float], store: dict) -> list[str]:
    scored = [
        (name, cosine_similarity(query_vector, vector))
        for name, vector in zip(store["names"], store["doc_vectors"])
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [name for name, _ in scored]


def sparse_ranking(query: str, store: dict) -> list[str]:
    query_tokens = tokenize(query)
    token_lists = store["token_lists"]
    avg_len = sum(len(doc) for doc in token_lists) / len(token_lists)
    scored = []
    for name, doc_tokens in zip(store["names"], token_lists):
        doc_len = len(doc_tokens)
        score = 0.0
        for term in query_tokens:
            tf = doc_tokens.count(term)
            if tf == 0:
                continue
            numerator = tf * (K1 + 1)
            denominator = tf + K1 * (1 - B + B * doc_len / avg_len)
            score += idf(term, token_lists) * (numerator / denominator)
        scored.append((name, score))
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [name for name, _ in scored]


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = RRF_K) -> list[str]:
    rrf_scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, name in enumerate(ranking, start=1):
            rrf_scores[name] = rrf_scores.get(name, 0.0) + 1 / (k + rank)
    return sorted(rrf_scores, key=lambda name: rrf_scores[name], reverse=True)


def hybrid_retrieve(query: str, store: dict, k: int = 2) -> list[str]:
    query_vector = embed_texts([query])[0]
    dense = dense_ranking(query_vector, store)
    sparse = sparse_ranking(query, store)
    fused = reciprocal_rank_fusion([dense, sparse])
    return fused[:k]


def generate(query: str, top_names: list[str], store: dict) -> str:
    text_by_name = dict(zip(store["names"], store["texts"]))
    context = "\n\n".join(f"[{name}]\n{text_by_name[name]}" for name in top_names)
    prompt = f"""Answer the question using only the context below. Cite the
source file in brackets. If the context doesn't contain the answer, say
so, don't guess.

Context:
{context}

Question: {query}"""
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text or ""


def ask(query: str, store: dict, k: int = 2) -> str:
    top_names = hybrid_retrieve(query, store, k)
    return generate(query, top_names, store)


def main() -> None:
    store = build_store(NOTES_DIR)
    print(f"Loaded {len(store['names'])} notes, built one dense index and one sparse index\n")

    questions = [
        "8 Nm",
        "20240115",
        "Why does my espresso taste weak and sour lately?",
        "Why do vertical walls have ridges even though I didn't change any settings?",
    ]

    for question in questions:
        answer = ask(question, store)
        print(f"Q: {question}")
        print(f"A: {answer}\n")


if __name__ == "__main__":
    main()
