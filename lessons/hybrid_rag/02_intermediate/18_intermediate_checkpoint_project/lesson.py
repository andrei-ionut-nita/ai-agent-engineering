"""
Lesson 18: Intermediate Checkpoint - Persisted, Filterable Hybrid
Notes-Search Assistant.

No new concepts, this combines Lessons 10-17 into one small script.
Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/02_intermediate/18_intermediate_checkpoint_project/lesson.py
"""

import json
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
STORE_PATH = Path(__file__).parent / "store.json"

CATEGORY = {
    "home_network.md": "network",
    "old_travel_router.md": "network",
    "3d_printer.md": "maker",
    "espresso_machine.md": "kitchen",
    "houseplants.md": "garden",
    "bike_maintenance.md": "outdoor",
}


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


def load_or_build_store(notes_dir: Path, store_path: Path) -> dict:
    if store_path.exists():
        return json.loads(store_path.read_text())
    store = build_store(notes_dir)
    store_path.write_text(json.dumps(store))
    return store


def hybrid_retrieve(query: str, store: dict, k: int = 2, category: str | None = None) -> list[str]:
    candidate_indices = [
        i for i, name in enumerate(store["names"])
        if category is None or CATEGORY.get(name) == category
    ]
    names = [store["names"][i] for i in candidate_indices]
    token_lists = [store["token_lists"][i] for i in candidate_indices]
    doc_vectors = [store["doc_vectors"][i] for i in candidate_indices]

    query_vector = embed_texts([query])[0]

    dense_scored = sorted(
        zip(names, (cosine_similarity(query_vector, v) for v in doc_vectors)),
        key=lambda pair: pair[1], reverse=True,
    )
    dense_ranking = [name for name, _ in dense_scored]

    query_tokens = tokenize(query)
    avg_len = sum(len(doc) for doc in token_lists) / len(token_lists)
    sparse_scored = []
    for name, doc_tokens in zip(names, token_lists):
        doc_len = len(doc_tokens)
        score = 0.0
        for term in query_tokens:
            tf = doc_tokens.count(term)
            if tf == 0:
                continue
            numerator = tf * (K1 + 1)
            denominator = tf + K1 * (1 - B + B * doc_len / avg_len)
            score += idf(term, token_lists) * (numerator / denominator)
        sparse_scored.append((name, score))
    sparse_scored.sort(key=lambda pair: pair[1], reverse=True)
    sparse_ranking = [name for name, _ in sparse_scored]

    rrf_scores: dict[str, float] = {}
    for ranking in (dense_ranking, sparse_ranking):
        for rank, name in enumerate(ranking, start=1):
            rrf_scores[name] = rrf_scores.get(name, 0.0) + 1 / (RRF_K + rank)
    fused = sorted(rrf_scores, key=lambda name: rrf_scores[name], reverse=True)
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


def ask(query: str, store: dict, k: int = 2, category: str | None = None) -> str:
    top_names = hybrid_retrieve(query, store, k, category)
    return generate(query, top_names, store)


def main() -> None:
    was_cached = STORE_PATH.exists()
    store = load_or_build_store(NOTES_DIR, STORE_PATH)
    print(f"Loaded {len(store['names'])} notes ({'from cache' if was_cached else 'freshly indexed'})\n")

    print("Q: 20240115")
    print(f"A: {ask('20240115', store)}\n")

    print("Q: Which build is the stable one? (scoped to category='network')")
    print(f"A: {ask('Which build is the stable one?', store, category='network')}\n")

    print("Q: Why do vertical walls have ridges even though I didn't change any settings?")
    print(f"A: {ask('Why do vertical walls have ridges even though I did not change any settings?', store)}\n")


if __name__ == "__main__":
    main()
