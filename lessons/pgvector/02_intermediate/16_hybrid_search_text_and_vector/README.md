# Lesson 16: Hybrid search, combining keyword and vector search in one query

## Where we left off

Every search since Lesson 5 has been purely semantic: rank by meaning,
ignore exact words. That's a real weakness for certain queries, an
exact product code, a person's name, a specific technical term, where a
user genuinely wants an exact keyword match, and semantic similarity
alone might rank a *related* chunk above the one containing the exact
term they typed. **Hybrid search** runs both kinds of search and
combines them, playing to each one's strengths.

## Postgres already has full-text search built in

```sql
content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
```

A `tsvector` is Postgres's own built-in representation for full-text
search: your text, normalized (lowercased, stemmed, stripped of common
words like "the"). `GENERATED ALWAYS AS (...) STORED` means Postgres
maintains this column automatically, every insert or update to
`content` recomputes it, no separate embedding-style step required,
this is plain Postgres, nothing pgvector-specific.

```sql
SELECT content, ts_rank(content_tsv, plainto_tsquery('english', %s)) AS rank
FROM notes
ORDER BY rank DESC
```

`plainto_tsquery` turns a plain search string into a query Postgres's
text search understands; `ts_rank` scores how well a row matches it.
Search for `"yeast"` and only the recipe chunk scores above zero, exact
word matching, unlike every vector search in this course so far.

## Where each one wins

- **Vector search** (`<=>`) wins when the right words aren't present at
  all, "baking bread" finding the pizza dough chunk, from Lesson 5
  onward.
- **Full-text search** (`ts_rank`) wins when the exact word matters and
  should count for a lot, searching `"yeast"` should surface the one
  chunk that says it, confidently, even if some other chunk is a close
  semantic neighbor.

## Combining both into one score

```sql
SELECT
    content,
    (1 - (embedding <=> %s)) * 0.5
      + ts_rank(content_tsv, plainto_tsquery('english', %s)) * 0.5 AS score
FROM notes
ORDER BY score DESC
LIMIT %s
```

`1 - cosine_distance` turns "smaller is better" into "bigger is
better" (a similarity, not a distance), so it combines sensibly with
`ts_rank` (which is already "bigger is better"). The `0.5` / `0.5`
split is a starting point, not a law, weighting text matches more
heavily makes sense for a product search box, weighting vector
similarity more heavily makes sense for an open-ended question,
answering a system like this, tune the two weights against real
queries from real users.

## Running it

```bash
docker compose up -d
uv run python lessons/pgvector/02_intermediate/16_hybrid_search_text_and_vector/lesson.py
```

## Checkpoint

- **`tsvector`** / **`to_tsvector`**: Postgres's own built-in full-text
  search representation, no extension needed.
- **`ts_rank`** / **`plainto_tsquery`**: score and parse a full-text
  search query.
- **hybrid search**: combine a normalized vector similarity with a
  text-search rank into one weighted score, tuned per use case.

If anything here still feels unclear, ask before moving to Lesson 17.
