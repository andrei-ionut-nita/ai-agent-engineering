"""
Lesson 17: reciprocal rank fusion, merging two ranked result lists
without needing their scores to share a scale.

Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/02_intermediate/17_reranking_results/lesson.py
"""

import os
from pathlib import Path

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


def load_chunks() -> list[str]:
    text = NOTES_PATH.read_text()
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    return splitter.split_text(text)


def reciprocal_rank_fusion(*rankings: list[int], k: int = 60) -> dict[int, float]:
    scores: dict[int, float] = {}
    for ranking in rankings:
        for rank, note_id in enumerate(ranking, start=1):
            scores[note_id] = scores.get(note_id, 0.0) + 1 / (k + rank)
    return scores


def main() -> None:
    chunks = load_chunks()
    embeddings_model = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        output_dimensionality=EMBEDDING_DIMENSIONS,
    )
    vectors = embeddings_model.embed_documents(chunks)

    dsn = os.environ["POSTGRES_DSN"]
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(conn)

        conn.execute("DROP TABLE IF EXISTS notes")
        conn.execute(
            f"""
            CREATE TABLE notes (
                id bigserial PRIMARY KEY,
                content text NOT NULL,
                embedding vector({EMBEDDING_DIMENSIONS}),
                content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
            )
            """
        )
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO notes (content, embedding) VALUES (%s, %s)",
                [(chunk, Vector(vector)) for chunk, vector in zip(chunks, vectors)],
            )

        content_by_id = dict(conn.execute("SELECT id, content FROM notes").fetchall())

        query = "yeast"
        query_vector = Vector(embeddings_model.embed_query(query))

        # Two independent rankings, in their own native units, over
        # the SAME set of documents.
        vector_ranking = [
            row[0]
            for row in conn.execute(
                "SELECT id FROM notes ORDER BY embedding <=> %s LIMIT 6",
                (query_vector,),
            ).fetchall()
        ]
        text_ranking = [
            row[0]
            for row in conn.execute(
                """
                SELECT id FROM notes
                ORDER BY ts_rank(content_tsv, plainto_tsquery('english', %s)) DESC
                LIMIT 6
                """,
                (query,),
            ).fetchall()
        ]

        print(f"Vector ranking (by id): {vector_ranking}")
        print(f"Text ranking (by id):   {text_ranking}\n")

        fused_scores = reciprocal_rank_fusion(vector_ranking, text_ranking)
        fused_ranking = sorted(fused_scores.items(), key=lambda item: item[1], reverse=True)

        print("Fused ranking (reciprocal rank fusion):")
        for note_id, score in fused_ranking:
            print(f"  rrf_score={score:.4f}  {content_by_id[note_id].splitlines()[0]}...")


if __name__ == "__main__":
    main()
