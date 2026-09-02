"""
Lesson 11: recomposing context from only the relevant strips, instead
of keeping or discarding a whole chunk.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/corrective_rag/02_intermediate/11_recomposing_context_from_relevant_strips/lesson.py
"""

import re
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"
NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"


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

QUESTION = "How often does the wind speed sensor need re-oiling?"
SOURCE = "weather-station.md"

GRADE_PROMPT = """You are grading whether a single sentence is relevant \
enough to help answer a question. Respond with exactly one word: \
"relevant" or "not_relevant".

Question: {question}

Sentence:
{sentence}"""


def split_into_strips(text: str) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    strips = []
    for paragraph in paragraphs:
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        strips.extend(s.strip() for s in sentences if s.strip())
    return strips


def grade_strip(question: str, strip: str) -> str:
    prompt = GRADE_PROMPT.format(question=question, sentence=strip)
    grade = call_model(prompt).strip().lower()
    return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"


def recompose(question: str, chunk_text: str) -> str:
    # Knowledge refinement, in miniature: split the chunk, grade every
    # strip, keep only the ones graded relevant, and glue them back into
    # one shorter piece of text, in their original order. This is the
    # paper's "correct" action, refine what's kept, don't just pass the
    # whole chunk through.
    strips = split_into_strips(chunk_text)
    relevant_strips = [s for s in strips if grade_strip(question, s) == "relevant"]
    return " ".join(relevant_strips)


def generate_answer(query: str, context: str) -> str:
    prompt = f"""Answer the question using only the context below. If the
context doesn't contain the answer, say so, don't guess.

Context:
{context}

Question: {query}"""
    return call_model(prompt)


def main() -> None:
    chunk_text = (NOTES_DIR / SOURCE).read_text()

    print(f"Q: {QUESTION}\n")

    whole_chunk_answer = generate_answer(QUESTION, chunk_text)
    print(f"Whole chunk as context ({len(chunk_text)} chars):")
    print(f"  {whole_chunk_answer}\n")

    recomposed = recompose(QUESTION, chunk_text)
    print(f"Recomposed context, relevant strips only ({len(recomposed)} chars):")
    print(f"  {recomposed!r}\n")

    recomposed_answer = generate_answer(QUESTION, recomposed)
    print(f"Answer from recomposed context:")
    print(f"  {recomposed_answer}")

    reduction = 100 * (1 - len(recomposed) / len(chunk_text))
    print(
        f"\nContext shrank by {reduction:.0f}% ({len(chunk_text)} -> "
        f"{len(recomposed)} chars), with the same answer, because the "
        "one sentence that actually matters is all that survived "
        "recomposition. Less context, same signal."
    )


if __name__ == "__main__":
    main()
