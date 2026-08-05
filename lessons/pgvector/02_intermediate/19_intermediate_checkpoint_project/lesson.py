"""
Lesson 19: Intermediate Checkpoint - Hybrid Search API.

No new concepts, this combines Lessons 10-18 into one small service.
Read README.md in this folder first, then read this file top to bottom,
then run it with (make sure Postgres is running first):

    docker compose up -d
    uv run python lessons/pgvector/02_intermediate/19_intermediate_checkpoint_project/lesson.py
"""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pgvector.psycopg import register_vector
from pgvector.utils import Vector
from psycopg_pool import ConnectionPool

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
CATEGORIES = ["project", "garden", "garden", "recipe", "household", "hobby"]


def reciprocal_rank_fusion(*rankings: list[str], k: int = 60) -> dict[str, float]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1 / (k + rank)
    return scores


class NotesSearchService:
    def __init__(self, dsn: str) -> None:
        # The extension must exist BEFORE the pool opens its first
        # connections, register_vector (below) needs to look up the
        # vector type, which only exists once the extension is enabled.
        with psycopg.connect(dsn, autocommit=True) as bootstrap_conn:
            bootstrap_conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

        # configure runs on every connection the pool opens, so each one
        # (not just the first) knows how to translate the vector type.
        self.pool = ConnectionPool(
            conninfo=dsn, min_size=2, max_size=10, configure=register_vector
        )
        self.pool.wait()
        self.embeddings_model = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            output_dimensionality=EMBEDDING_DIMENSIONS,
        )
        with self.pool.connection() as conn:
            conn.execute("DROP TABLE IF EXISTS notes")
            conn.execute(
                f"""
                CREATE TABLE notes (
                    external_id text PRIMARY KEY,
                    content text NOT NULL,
                    category text NOT NULL,
                    embedding vector({EMBEDDING_DIMENSIONS}),
                    content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
                )
                """
            )

    def upsert_notes(self, notes: list[dict]) -> None:
        vectors = self.embeddings_model.embed_documents([note["content"] for note in notes])
        with self.pool.connection() as conn, conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO notes (external_id, content, category, embedding)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (external_id) DO UPDATE
                SET content = EXCLUDED.content,
                    category = EXCLUDED.category,
                    embedding = EXCLUDED.embedding
                """,
                [
                    (note["external_id"], note["content"], note["category"], Vector(vector))
                    for note, vector in zip(notes, vectors)
                ],
            )

    def build_index(self) -> None:
        with self.pool.connection() as conn:
            conn.execute("DROP INDEX IF EXISTS notes_embedding_idx")
            conn.execute(
                "CREATE INDEX notes_embedding_idx ON notes USING hnsw (embedding vector_cosine_ops)"
            )

    def search(self, query: str, k: int = 3) -> list[tuple[str, float]]:
        query_vector = Vector(self.embeddings_model.embed_query(query))
        with self.pool.connection() as conn:
            vector_ranking = [
                row[0]
                for row in conn.execute(
                    "SELECT external_id FROM notes ORDER BY embedding <=> %s LIMIT 6",
                    (query_vector,),
                ).fetchall()
            ]
            text_ranking = [
                row[0]
                for row in conn.execute(
                    """
                    SELECT external_id FROM notes
                    ORDER BY ts_rank(content_tsv, plainto_tsquery('english', %s)) DESC
                    LIMIT 6
                    """,
                    (query,),
                ).fetchall()
            ]
            content_by_id = dict(conn.execute("SELECT external_id, content FROM notes").fetchall())

        fused = reciprocal_rank_fusion(vector_ranking, text_ranking)
        ranked = sorted(fused.items(), key=lambda item: item[1], reverse=True)[:k]
        return [(content_by_id[doc_id], score) for doc_id, score in ranked]

    def close(self) -> None:
        self.pool.close()


def load_chunks() -> list[str]:
    text = NOTES_PATH.read_text()
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    return splitter.split_text(text)


def main() -> None:
    chunks = load_chunks()
    notes = [
        {"external_id": f"note-{i}", "content": chunk, "category": category}
        for i, (chunk, category) in enumerate(zip(chunks, CATEGORIES))
    ]

    service = NotesSearchService(os.environ["POSTGRES_DSN"])
    try:
        service.upsert_notes(notes)
        service.build_index()
        print(f"Ingested and indexed {len(notes)} notes.\n")

        # Re-ingest one note with edited content, same external_id: the
        # upsert path should update it AND re-embed it, not just error
        # or create a duplicate row.
        notes[3]["content"] = (
            "Recipe notes: switched entirely to sourdough starter, no commercial yeast."
        )
        service.upsert_notes([notes[3]])
        print("Re-ingested note-3 with edited content (upsert, re-embedded).\n")

        results = service.search("yeast", k=3)
        print("Hybrid search for 'yeast':")
        for content, score in results:
            print(f"  rrf_score={score:.4f}  {content.splitlines()[0]}...")
    finally:
        service.close()


if __name__ == "__main__":
    main()
