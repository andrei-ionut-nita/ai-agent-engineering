"""
Lesson 13: normalizing vectors, and why the choice of distance metric
matters, a toy example where cosine and inner product actually disagree.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/02_intermediate/13_choosing_a_distance_metric/lesson.py
"""

import os
from pathlib import Path

import numpy as np
import psycopg
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pgvector.psycopg import register_vector
from pgvector.utils import Vector

load_dotenv()

NOTES_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "langchain"
    / "03_advanced"
    / "27_document_loading_and_splitting"
    / "data"
    / "notes.txt"
)
EMBEDDING_DIMENSIONS = 768


def toy_example(conn: psycopg.Connection) -> None:
    conn.execute("DROP TABLE IF EXISTS toy")
    conn.execute("CREATE TABLE toy (label text, embedding vector(2))")

    query = Vector([1.0, 0.0])
    # Same direction as the query, but a small magnitude.
    conn.execute(
        "INSERT INTO toy VALUES (%s, %s)", ("close_direction_small", Vector([0.1, 0.0]))
    )
    # A somewhat different direction, but a large magnitude.
    conn.execute(
        "INSERT INTO toy VALUES (%s, %s)", ("off_direction_large", Vector([0.9, 0.436]))
    )

    print("Toy example: query = [1.0, 0.0]\n")
    for label, operator in [
        ("cosine distance (<=>)", "<=>"),
        ("negative inner product (<#>)", "<#>"),
        ("L2 distance (<->)", "<->"),
    ]:
        rows = conn.execute(
            f"SELECT label, embedding {operator} %s AS distance FROM toy ORDER BY distance",
            (query,),
        ).fetchall()
        ranking = " then ".join(f"{r[0]} ({r[1]:.4f})" for r in rows)
        print(f"{label}: {ranking}")

    print(
        "\nNotice the ranking flips: cosine correctly ranks "
        "'close_direction_small' first (it points in the EXACT same "
        "direction as the query), but raw inner product ranks "
        "'off_direction_large' first instead, purely because it's a "
        "longer vector.\n"
    )


def real_embeddings_have_similar_norms() -> None:
    text = NOTES_PATH.read_text()
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    chunks = splitter.split_text(text)

    embeddings_model = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        output_dimensionality=EMBEDDING_DIMENSIONS,
    )
    vectors = embeddings_model.embed_documents(chunks)
    norms = [float(np.linalg.norm(v)) for v in vectors]

    print("Real Gemini embedding norms, one per notes.txt chunk:")
    for i, norm in enumerate(norms):
        print(f"  chunk {i}: {norm:.4f}")
    print(
        "\nAll close together, unlike the toy example above. This is why "
        "<#> often works fine in practice for one model's own output, "
        "but normalizing (dividing each vector by its own norm) removes "
        "the risk entirely, and is required the moment vectors from "
        "different sources ever get mixed in the same table."
    )


def main() -> None:
    dsn = os.environ["POSTGRES_DSN"]
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(conn)
        toy_example(conn)

    real_embeddings_have_similar_norms()


if __name__ == "__main__":
    main()
