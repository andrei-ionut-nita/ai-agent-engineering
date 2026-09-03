"""
Lesson 22 (optional): wiring a relevance grader, the same idea
corrective_rag builds a whole course around, in as a fourth tool this
agent can call to double-check a retrieved passage before trusting it.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/03_advanced/22_optional_corrective_grading_as_a_tool/lesson.py
"""

import ast
import math
import operator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"
MAX_STEPS = 5

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

SYSTEM_INSTRUCTION = """You answer questions using a notes search tool. After
calling search_notes, if you are not confident the returned passage
actually answers the question, call grade_passage to check before
relying on it. If grade_passage says a passage is not relevant, try
search_notes again with a different query rather than answering from an
ungraded or poorly-graded passage."""


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


def build_vector_store() -> list[dict]:
    paths = sorted(NOTES_DIR.glob("*.md"))
    texts = [path.read_text() for path in paths]
    vectors = embed_texts(texts)
    return [
        {"text": text, "embedding": vector, "source": path.name}
        for path, text, vector in zip(paths, texts, vectors)
    ]


def search_notes(query: str, store: list[dict], k: int = 1) -> str:
    query_vector = embed_texts([query])[0]
    scored = [
        {**record, "score": cosine_similarity(query_vector, record["embedding"])}
        for record in store
    ]
    scored.sort(key=lambda record: record["score"], reverse=True)
    top_k = scored[:k]
    return "\n\n---\n\n".join(f"[{r['source']}]\n{r['text']}" for r in top_k)


def get_current_datetime(timezone: str) -> str:
    tz = ZoneInfo(timezone)
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M %Z")


_CALC_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}


def calculate(expression: str) -> str:
    node = ast.parse(expression, mode="eval").body

    def _eval(n: ast.AST) -> float:
        if isinstance(n, ast.BinOp) and type(n.op) in _CALC_OPS:
            return _CALC_OPS[type(n.op)](_eval(n.left), _eval(n.right))
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        raise ValueError(f"Unsupported expression: {expression!r}")

    return str(_eval(node))


# The same binary relevance grade corrective_rag Lesson 3
# (lessons/corrective_rag/01_beginner/03_grading_a_retrieved_chunk)
# introduces, self-contained here rather than imported, since this
# course doesn't depend on corrective_rag existing to run. The idea,
# not the code, is what's being cross-referenced.
GRADE_PROMPT = """You are grading whether a retrieved passage is relevant \
enough to help answer a question. Read the question and the passage, \
then respond with exactly one word: "relevant" or "not_relevant".

Question: {question}

Passage:
{passage}"""


def grade_passage(question: str, passage: str) -> str:
    prompt = GRADE_PROMPT.format(question=question, passage=passage)
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    grade = (response.text or "").strip().lower()
    return "relevant" if "not_relevant" not in grade and "relevant" in grade else "not_relevant"


@dataclass
class Tool:
    declaration: types.FunctionDeclaration
    fn: Callable[..., str]


def build_registry(store: list[dict]) -> dict[str, Tool]:
    return {
        "search_notes": Tool(
            declaration=types.FunctionDeclaration(
                name="search_notes",
                description="Search a personal notes collection for passages relevant to a query.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={"query": types.Schema(type=types.Type.STRING, description="What to search for.")},
                    required=["query"],
                ),
            ),
            fn=lambda query: search_notes(query, store),
        ),
        "get_current_datetime": Tool(
            declaration=types.FunctionDeclaration(
                name="get_current_datetime",
                description="Get the current date and time in a named IANA timezone.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={"timezone": types.Schema(type=types.Type.STRING, description="An IANA timezone name.")},
                    required=["timezone"],
                ),
            ),
            fn=get_current_datetime,
        ),
        "calculate": Tool(
            declaration=types.FunctionDeclaration(
                name="calculate",
                description="Evaluate a basic arithmetic expression.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={"expression": types.Schema(type=types.Type.STRING, description="An arithmetic expression.")},
                    required=["expression"],
                ),
            ),
            fn=calculate,
        ),
        "grade_passage": Tool(
            declaration=types.FunctionDeclaration(
                name="grade_passage",
                description=(
                    "Check whether a passage you already retrieved with "
                    "search_notes is actually relevant to a question. "
                    "Returns 'relevant' or 'not_relevant'. Use this when "
                    "you're unsure a retrieved passage really answers the "
                    "question before relying on it."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "question": types.Schema(type=types.Type.STRING, description="The original question."),
                        "passage": types.Schema(type=types.Type.STRING, description="The retrieved passage text to check."),
                    },
                    required=["question", "passage"],
                ),
            ),
            fn=grade_passage,
        ),
    }


def run_agent(query: str, registry: dict[str, Tool], max_steps: int = MAX_STEPS) -> str:
    declarations = [tool.declaration for tool in registry.values()]
    config = types.GenerateContentConfig(
        tools=[types.Tool(function_declarations=declarations)], system_instruction=SYSTEM_INSTRUCTION
    )
    contents: list[types.Content] = [types.Content(role="user", parts=[types.Part(text=query)])]

    for _ in range(max_steps):
        response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=config)
        calls = response.function_calls
        if not calls:
            return response.text or ""

        call = calls[0]
        tool = registry.get(call.name)
        if tool is None:
            result = {"error": f"Unknown tool: {call.name}"}
        else:
            try:
                result = {"output": tool.fn(**(call.args or {}))}
            except Exception as error:
                result = {"error": f"{type(error).__name__}: {error}"}

        assert response.candidates is not None
        contents.append(response.candidates[0].content)
        contents.append(
            types.Content(role="user", parts=[types.Part.from_function_response(name=call.name, response=result)])
        )

    return "I wasn't able to fully answer this within the allowed number of search steps."


def main() -> None:
    store = build_vector_store()
    registry = build_registry(store)

    question = "How often does the aquarium's filter sponge get rinsed?"
    print(f"Q: {question}")
    print(f"A: {run_agent(question, registry)}\n")

    print(
        "grade_passage() is an optional fourth tool, not a required part of\n"
        "this course's core loop, its whole job is letting the agent catch\n"
        "its own bad retrieval before answering from it, the same problem\n"
        "corrective_rag's entire course solves as a fixed pipeline stage that\n"
        "runs on every single retrieval. Here it's the model's own choice\n"
        "whether to bother double-checking at all."
    )


if __name__ == "__main__":
    main()
