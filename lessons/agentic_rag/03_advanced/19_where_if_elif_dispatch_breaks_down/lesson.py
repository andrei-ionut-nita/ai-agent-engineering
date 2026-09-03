"""
Lesson 19: adding a third tool to the if/elif dispatch chain, and
watching the specific way it breaks when a branch gets forgotten.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/03_advanced/19_where_if_elif_dispatch_breaks_down/lesson.py
"""

import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"

NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"


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


def calculate(expression: str) -> str:
    # A trivial calculator, evaluated safely via Python's ast module
    # (no eval()/exec()), used starting Lesson 21. Declared here
    # already, deliberately, so this lesson can demonstrate what
    # happens when a tool is DECLARED to the model but its dispatch
    # branch is forgotten, a realistic way this breaks in practice.
    import ast
    import operator

    ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}
    node = ast.parse(expression, mode="eval").body

    def _eval(n):
        if isinstance(n, ast.BinOp) and type(n.op) in ops:
            return ops[type(n.op)](_eval(n.left), _eval(n.right))
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        raise ValueError(f"Unsupported expression: {expression!r}")

    return str(_eval(node))


SEARCH_NOTES_DECLARATION = types.FunctionDeclaration(
    name="search_notes",
    description="Search a personal notes collection for passages relevant to a query.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={"query": types.Schema(type=types.Type.STRING, description="What to search for.")},
        required=["query"],
    ),
)

GET_CURRENT_DATETIME_DECLARATION = types.FunctionDeclaration(
    name="get_current_datetime",
    description="Get the current date and time in a named IANA timezone.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={"timezone": types.Schema(type=types.Type.STRING, description="An IANA timezone name.")},
        required=["timezone"],
    ),
)

CALCULATE_DECLARATION = types.FunctionDeclaration(
    name="calculate",
    description="Evaluate a basic arithmetic expression, e.g. '12 * 8' or '240 / 4'.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={"expression": types.Schema(type=types.Type.STRING, description="An arithmetic expression.")},
        required=["expression"],
    ),
)

# All THREE tools declared to the model.
TOOLS = types.Tool(
    function_declarations=[SEARCH_NOTES_DECLARATION, GET_CURRENT_DATETIME_DECLARATION, CALCULATE_DECLARATION]
)
CONFIG = types.GenerateContentConfig(tools=[TOOLS])


def run_tool_incomplete(call: types.FunctionCall, store: list[dict]) -> str:
    # The exact if/elif shape every Beginner-tier lesson used, extended
    # to three tools, EXCEPT the third branch was never added, an easy
    # mistake: the declaration above was added, but the matching
    # dispatch branch here was not, and nothing catches that mismatch
    # until a question actually needs the missing tool.
    if call.name == "search_notes":
        return search_notes(call.args["query"], store)
    elif call.name == "get_current_datetime":
        return get_current_datetime(call.args["timezone"])
    else:
        raise ValueError(f"Unknown tool: {call.name}")


def ask(query: str, store: list[dict]) -> str:
    contents: list[types.Content] = [types.Content(role="user", parts=[types.Part(text=query)])]
    response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=CONFIG)

    calls = response.function_calls
    if not calls:
        return response.text or ""

    call = calls[0]
    result = run_tool_incomplete(call, store)  # raises if the model picked "calculate"

    assert response.candidates is not None
    contents.append(response.candidates[0].content)
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_function_response(name=call.name, response={"result": result})],
        )
    )
    final_response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=CONFIG)
    return final_response.text or ""


def main() -> None:
    store = build_vector_store()
    question = "What is 240 divided by 4?"

    print(f"Q: {question}")
    print(
        "Three tools are declared to the model (search_notes, get_current_datetime,\n"
        "calculate), but run_tool_incomplete()'s if/elif chain only handles the\n"
        "first two, calculate's declaration exists, but nothing wires it to the\n"
        "real calculate() function above.\n"
    )
    try:
        answer = ask(question, store)
        print(f"A: {answer}")
    except ValueError as error:
        print(f"Crashed: {error}")
        print(
            "\nThis is exactly the bug a growing if/elif chain invites: every new\n"
            "tool needs its declaration added in ONE place (the Tool list) and its\n"
            "dispatch logic added in a SEPARATE place (the if/elif chain), and\n"
            "nothing in the code connects the two or warns you if you forget one.\n"
            "It compiles, it runs, it even answers other questions correctly, and\n"
            "then crashes the moment a real user asks something that needs the\n"
            "one tool whose branch got missed."
        )


if __name__ == "__main__":
    main()
