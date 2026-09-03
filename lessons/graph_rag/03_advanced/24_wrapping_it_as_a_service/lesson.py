"""
Lesson 24: wrapping Lesson 23's ingest()/ask() as a small FastAPI
service. Same pattern as naive_rag Lesson 24, see that lesson's README
for the fuller FastAPI walkthrough, this file only differs in what
State holds.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/03_advanced/24_wrapping_it_as_a_service/lesson.py

To run this as a real, live server instead:

    uvicorn lesson:app --reload
"""

import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import NamedTuple

import chromadb
import networkx as nx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

client = genai.Client()

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
CHAT_MODEL = "gemini-3.5-flash-lite"
NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"


class State(NamedTuple):
    graph: nx.DiGraph
    collection: chromadb.Collection


def extract_relationships(text: str) -> list[tuple[str, str, str]]:
    prompt = f"""You are extracting relationships for a knowledge graph.

Read the text below and list EVERY relationship between two entities as
a (subject, relation, object) triple, including actions one entity took
regarding another (e.g. "flagged as drifting", "noticed", "pulled",
"recalibrated"), not just static facts. Be thorough: aim for at least
one triple per sentence that mentions two or more entities.

When a sentence describes an action about something already named
earlier in the text, use that thing's established full name as the
subject or object, not a pronoun, a paraphrase, or an abstract noun
like "drift" or "the issue." For example, if "the humidity sensor" was
already introduced, "Dev flagged it as drifting" should produce
("Dev", "flagged as drifting", "humidity sensor"), not
("Dev", "flagged", "drift").

The subject and object should be short entity names (people, places,
specific things), and the relation should be a short verb phrase
(2-4 words).

Return ONLY a JSON array of 3-element arrays, like:
[["Mia", "recalibrated", "humidity sensor"], ["multimeter", "kept in", "garage bench"]]

Text:
{text}"""
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json", temperature=0
        ),
    )
    assert response.text is not None
    triples = json.loads(response.text)
    return [tuple(triple) for triple in triples]


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
    assert response.embeddings is not None
    return [e.values for e in response.embeddings if e.values is not None]


def gather_facts(graph: nx.DiGraph, start: str, max_hops: int = 3) -> list[str]:
    facts: list[str] = []
    frontier = {start}
    visited = {start}
    for _ in range(max_hops):
        next_frontier = set()
        for node in frontier:
            if node not in graph:
                continue
            for _, other, data in graph.out_edges(node, data=True):
                facts.append(f"{node} {data['relation']} {other}")
                if other not in visited:
                    next_frontier.add(other)
                    visited.add(other)
            for other, _, data in graph.in_edges(node, data=True):
                facts.append(f"{other} {data['relation']} {node}")
                if other not in visited:
                    next_frontier.add(other)
                    visited.add(other)
        frontier = next_frontier
    return facts


def generate_answer(query: str, facts: list[str]) -> str:
    if not facts:
        return "I don't have any information relevant to that question."
    context = "\n".join(facts)
    prompt = f"""You are answering a question using facts gathered by
traversing a knowledge graph, not a single passage of prose. The facts
are short (subject, relation, object) statements, listed in the order
traversal found them; facts about the same entity that appear near each
other usually describe the same underlying event. Combine them into a
single coherent answer using only what the facts support. If a specific
detail genuinely isn't supported by any fact, say so plainly instead of
guessing.

Facts:
{context}

Question: {query}"""
    response = client.models.generate_content(model=CHAT_MODEL, contents=prompt)
    return response.text or ""


def ingest(docs: list[Path]) -> State:
    graph = nx.DiGraph()
    for path in docs:
        for subject, relation, obj in extract_relationships(path.read_text()):
            graph.add_edge(subject, obj, relation=relation)

    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="graph_nodes")
    node_names = list(graph.nodes())
    if node_names:
        collection.add(
            ids=node_names, documents=node_names, embeddings=embed_texts(node_names)
        )

    return State(graph=graph, collection=collection)


def ask(query: str, state: State, k: int = 2) -> str:
    query_vector = embed_texts([query])[0]
    results = state.collection.query(query_embeddings=[query_vector], n_results=1)
    ids = results["ids"]
    if not ids or not ids[0]:
        return "I don't have any information relevant to that question."
    start = ids[0][0]

    facts = gather_facts(state.graph, start, max_hops=3)
    return generate_answer(query, facts)


class AskResponse(BaseModel):
    answer: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ingest() runs once, at startup, exactly naive_rag Lesson 24's
    # pattern, storing this course's two-field State instead of a bare
    # chromadb.Collection.
    docs = sorted(NOTES_DIR.glob("*.md"))
    app.state.graph_state = ingest(docs)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/ask", response_model=AskResponse)
def ask_endpoint(q: str, k: int = 2) -> AskResponse:
    return AskResponse(answer=ask(q, app.state.graph_state, k))


def main() -> None:
    with TestClient(app) as test_client:
        for question in (
            "What's stored on the garage electronics bench?",
            "What is the capital of France?",
        ):
            response = test_client.get("/ask", params={"q": question})
            print(f"GET /ask?q={question!r}")
            print(f"  {response.json()}\n")


if __name__ == "__main__":
    main()
