# Lesson 3: The `vector(N)` column type, and getting Python lists in and out

## Where we left off

Lesson 1 enabled the `vector` extension. This lesson uses it: create a
table with a `vector` column, put a vector in, get it back out, as a
normal Python list.

## Declaring a vector column

```sql
CREATE TABLE items (
    id bigserial PRIMARY KEY,
    content text NOT NULL,
    embedding vector(3)
)
```

`vector(3)` means every value in this column is a fixed-length list of
exactly 3 floating point numbers. The number is not a default or a
maximum, it's an exact, enforced dimension: Postgres will reject an
insert of a 4-number vector into a `vector(3)` column. Real embedding
models produce much longer vectors (Gemini's `gemini-embedding-001`
produces 3072 numbers by default), 3 is used here only so the printed
output stays readable.

## The problem: Postgres doesn't know what a Python list is

Naively, you might expect `psycopg` to turn a Python list like
`[1.0, 2.0, 3.0]` into a `vector` automatically. It won't, a plain list
adapts to a Postgres *array* type by default, not a `vector`, and
inserting it will fail with a type mismatch. Two extra pieces close
this gap:

```python
from pgvector.psycopg import register_vector
from pgvector.utils import Vector

register_vector(conn)
```

`register_vector(conn)` (from the `pgvector` Python package, a
companion to the extension) teaches this specific connection how to
translate Postgres's `vector` type to and from Python. `Vector(...)` is
a thin wrapper you put around a Python list to say "adapt this one as a
`vector`, specifically."

```python
conn.execute(
    "INSERT INTO items (content, embedding) VALUES (%s, %s)",
    ("first item", Vector([1.0, 2.0, 3.0])),
)
```

## Getting it back out

```python
row = conn.execute("SELECT embedding FROM items WHERE id = 1").fetchone()
print(row[0])          # [1.0, 2.0, 3.0]
print(type(row[0]))     # <class 'numpy.ndarray'>
```

Once `register_vector` has run, reading a `vector` column back gives
you a NumPy array, not a Python list, NumPy is what the rest of the
Python data/ML ecosystem (including embedding models) already expects
vectors to look like.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/01_beginner/03_vector_column_and_type/lesson.py
```

## Checkpoint

- **`vector(N)`**: a column type holding a fixed-length, exact-dimension
  list of floats.
- **`register_vector(conn)`**: teaches one connection how to translate
  Postgres's `vector` type to and from Python.
- **`Vector([...])`**: wraps a Python list so `psycopg` adapts it as a
  `vector`, not a Postgres array.
- Values come back out as NumPy arrays, once `register_vector` has run.

If anything here still feels unclear, ask before moving to Lesson 4.
