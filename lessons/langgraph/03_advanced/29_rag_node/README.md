# Lesson 29: A retrieval node feeding a generation node

## Retrieval-augmented generation, minus the infrastructure

The langchain course's lessons 27-29 built RAG with real document
loaders, splitters, and a vector store. The underlying idea is simpler
than that infrastructure suggests: find the few pieces of text most
relevant to a question, then ask the model to answer using only those
pieces. This lesson keeps that idea, but skips the vector store, no new
dependency is needed to demonstrate why retrieval matters.

## A tiny local "document store"

```python
DOCUMENTS = [
    "The office recycling bins are collected every Tuesday and Friday morning.",
    "Employees get 20 days of paid vacation per year, accrued monthly.",
    ...
]
```

Just a Python list of strings. No embeddings API call, no database, this
is enough to prove the point: the generation node's answer quality
depends entirely on what the retrieval node hands it.

## The retrieval node

```python
def retrieve(state: State) -> dict:
    question_words = set(state["question"].lower().split())
    scored = sorted(
        DOCUMENTS,
        key=lambda doc: len(question_words & set(doc.lower().split())),
        reverse=True,
    )
    return {"retrieved": scored[:2]}
```

Deliberately simple keyword scoring: count how many words the question
and each document share, keep the top two. Real systems typically use
embeddings and vector similarity for this instead of exact word overlap,
but the *shape* of the step, "score every candidate, keep the best few,"
is identical either way.

## The generation node

```python
def generate(state: State) -> dict:
    context = "\n".join(f"- {doc}" for doc in state["retrieved"])
    prompt = (
        "Answer the question using ONLY the context below. If the context "
        "doesn't contain the answer, say you don't know.\n\n"
        f"Context:\n{context}\n\nQuestion: {state['question']}"
    )
    response = model.invoke(prompt)
    return {"answer": response.text}
```

`generate` never sees the full `DOCUMENTS` list, only whatever
`retrieve` decided was relevant, the same separation of concerns as any
two-node pipeline since Beginner Lesson 3. The instruction to answer
"using ONLY the context" is what makes the retrieval step actually
matter, without it, the model might just answer from its own general
knowledge and mask a bad retrieval.

## Running it

```bash
uv run python lessons/langgraph/03_advanced/29_rag_node/lesson.py
```

The last question asks about something no document mentions at all
("What is the office WiFi password?"). Watch the model correctly say it
doesn't know, because the instruction told it not to guess beyond the
retrieved context.

## Checkpoint

- **retrieval node**: scores candidate documents against a query, keeps
  the most relevant few.
- **generation node**: only sees what was retrieved, not the full
  document set, and is instructed to stay within it.
- **why keyword scoring is fine here**: the *pattern* (score, keep top
  k, generate from that) matters more for learning than the specific
  similarity method; production RAG usually swaps in embeddings.
- **"answer using ONLY the context"**: the instruction that makes bad
  retrieval visible instead of silently masked by the model's own
  knowledge.

If anything here still feels unclear, ask before moving to Lesson 30.
