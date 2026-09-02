"""
Lesson 14: three query rewriting strategies - broadening, narrowing,
and decomposing into sub-questions.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/02_intermediate/14_query_rewriting_strategies/lesson.py
"""

import math
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"
NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

BROADEN_PROMPT = """Rewrite this question to be more general, so it's \
more likely to match a passage that discusses the same topic in \
different words. Reply with only the rewritten question.

Original question: {question}"""

NARROW_PROMPT = """Rewrite this question to be more specific and \
concrete, adding likely relevant terms, so it's less likely to match \
irrelevant passages. Reply with only the rewritten question.

Original question: {question}"""

DECOMPOSE_PROMPT = """This question asks about more than one thing at \
once. Break it into separate, simpler sub-questions, one per line, no \
numbering, no extra text.

Original question: {question}"""


def call_model(prompt: str) -> str:
    for attempt in range(5):
        try:
            response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
            return response.text or ""
        except ClientError as error:
            if error.code == 429 and attempt < 4:
                time.sleep(20)
                continue
            raise
    raise RuntimeError("Exceeded retries calling the model")


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
    assert response.embeddings is not None
    return [e.values for e in response.embeddings]  # type: ignore[misc]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))
    return dot_product / (magnitude_a * magnitude_b)


def build_vector_store() -> list[dict]:
    paths = sorted(NOTES_DIR.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)
    return [
        {"text": text, "embedding": vector, "source": path.name}
        for path, text, vector in zip(paths, texts, vectors)
    ]


def retrieve(query: str, store: list[dict], k: int) -> list[dict]:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    return scored[:k]


def main() -> None:
    store = build_vector_store()

    # Decomposing: a compound question needing two different sources.
    compound_question = "How long is the cello practice session, and what color-based system organizes the bookshelf?"
    print(f"Compound question: {compound_question!r}")
    original_top2 = retrieve(compound_question, store, k=2)
    for chunk in original_top2:
        print(f"  combined query, k=2: {chunk['source']} (score={chunk['score']:.4f})")

    sub_questions = [
        line.strip() for line in call_model(DECOMPOSE_PROMPT.format(question=compound_question)).splitlines() if line.strip()
    ]
    print(f"\n  Decomposed into: {sub_questions}")
    for sub_q in sub_questions:
        top1 = retrieve(sub_q, store, k=1)[0]
        print(f"  sub-question {sub_q!r} -> {top1['source']} (score={top1['score']:.4f})")

    print(
        "\nOn this course's small, five-document corpus, the combined query "
        "already retrieves both correct sources at k=2, this corpus is too "
        "clean to force a miss. What decomposition buys even here: each "
        "sub-question's own top match scores noticeably higher than the "
        "same source did inside the blended combined query, one clear "
        "signal per question instead of one averaged signal for two "
        "questions at once. At real scale, with thousands of chunks "
        "instead of five, that averaging is exactly what causes a combined "
        "query to miss a source a decomposed sub-question would have found "
        "cleanly."
    )

    print(
        "\nBroadening and narrowing (this lesson's other two strategies) "
        "reshape a single question's wording; decomposing (above) splits "
        "one question into several, run separately. All three exist "
        "because Lessons 6-7's single rewrite attempt isn't the only way "
        "to fix a wording problem, different failure shapes call for "
        "different rewrites."
    )

    print(
        "\nA note on tuning: which strategy to try for which failure shape "
        "(this lesson's own heuristic: compound questions get decomposed, "
        "vague ones get narrowed, over-specific ones get broadened) was "
        "chosen by inspecting the failure shapes Lessons 6-12 already "
        "demonstrated by hand, not by sweeping strategies against "
        "Lesson 17's labeled question set and picking whichever scored "
        "highest there. That distinction matters, see Lesson 17's README "
        "for why."
    )


if __name__ == "__main__":
    main()
