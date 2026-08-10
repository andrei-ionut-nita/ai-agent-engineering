# Lesson 9: Beginner checkpoint project

## Everything so far, in one small program

This lesson doesn't introduce anything new. It's a checkpoint: a small
Q&A CLI over the same Nimbus Robotics policy docs Lesson 2 introduced,
built entirely from pieces this course's beginner tier already covered.

| Lesson | Concept used here |
|---|---|
| 2 | `SimpleDirectoryReader` loads Documents from `data/` |
| 3 | `Settings.llm` / `Settings.embed_model`, configured once, globally |
| 4 | `VectorStoreIndex.from_documents()` splits into Nodes and embeds them |
| 5 | `response.source_nodes` used to show which files backed an answer |
| 6 | (implicit) the retrieval step inside the chat engine's pipeline |
| 7 | (implicit) response synthesis, using the chat engine's default mode |
| 8 | `index.as_chat_engine()` and `.chat()`, memory across turns |

If any row in that table doesn't make sense on its own, that's the
signal to go back to that lesson before continuing past this one.

## Why a hardcoded question list instead of `input()`

A real CLI would read questions from `input()` in a loop. This lesson
uses a hardcoded `EXAMPLE_QUESTIONS` list instead, run through the same
`ask()` function, because a hardcoded list produces exactly
reproducible output to capture in a README, an `input()` loop's output
depends on what a person typed, which can't be captured ahead of time.

The code is structured so the swap is trivial: `build_engine()` and
`ask()` don't know or care where a question string came from. A
`run_interactive()` function at the bottom of `lesson.py` shows the
real `input()` version, it isn't called by `main()`, but reading it
shows the whole swap is two lines: replace the `for question in
EXAMPLE_QUESTIONS` loop with a `while True: input(...)` loop.

## The code, piece by piece

```python
def build_engine():
    documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()
    index = VectorStoreIndex.from_documents(documents)
    return index.as_chat_engine()
```

The full ingest -> index -> chat pipeline in three lines, Lessons 2, 4,
and 8 respectively.

```python
def ask(chat_engine, question: str) -> None:
    response = chat_engine.chat(question)
    print(f"Nimbus Assistant: {response.response.strip()}")
    sources = sorted({Path(n.metadata["file_name"]).name for n in response.source_nodes})
    print(f"  (sources: {', '.join(sources)})\n")
```

A `ChatEngine`'s response still carries `.source_nodes`, the same
attribute Lesson 5's `QueryEngine` response had. This function shows
both halves at once, the conversational answer and which policy files
actually backed it, tying Lesson 5's source-citation idea into Lesson
8's chat loop.

## Running it

```bash
uv run python lessons/llamaindex/01_beginner/09_beginner_checkpoint_project/lesson.py
```

## Expected output

Answer wording is LLM-generated and non-deterministic, your exact
phrasing will vary; source file lists should stay stable. Captured
from a real run:

```
Building index over Nimbus Robotics policy docs...

Running example questions (see run_interactive() for a real input() loop):

You:   What's the vacation policy for new hires?
Nimbus Assistant: Based on the Nimbus Robotics Vacation and Time Off Policy document, here are the specific details regarding new hires:
...
  (sources: remote_work_policy.txt, vacation_policy.txt)

You:   Can I still take time off if I've used up my first-90-days allowance?
Nimbus Assistant: Based on the Nimbus Robotics vacation policy documents, I do not know the answer to whether you can take additional time off if you have already used up your 5-day allowance during your first 90 days.
...
  (sources: remote_work_policy.txt, vacation_policy.txt)

You:   What about expense approval, does it depend on the amount?
Nimbus Assistant: Yes, absolutely! The expense reimbursement policy at Nimbus Robotics relies heavily on the specific monetary amount and the nature of the purchase.
...
  (sources: expense_policy.txt, remote_work_policy.txt)
```

(Full answers for all three questions are printed when you actually
run it, trimmed here for length.) Worth noticing on the second
question: the assistant honestly says the source documents don't
explicitly cover that edge case, "I do not know the answer to whether
you can take additional time off ..." rather than confidently
inventing a rule that isn't in `vacation_policy.txt`. That's the
retrieval + synthesis pipeline working as intended: it answers from
what the source_nodes actually contain, not from the model's own
assumptions.

## Checkpoint

This closes out the beginner tier. Recapping the whole arc:

- **Document -> Node -> Index -> QueryEngine/ChatEngine** (Lesson 1)
  is the shape every lesson since has been building toward.
- **`SimpleDirectoryReader`** loads Documents; **`SentenceSplitter`**
  (used internally by `VectorStoreIndex.from_documents`) splits them
  into Nodes (Lesson 2).
- **`Settings`** is the global object holding your LLM and embedding
  model, set once, read everywhere (Lesson 3).
- **`VectorStoreIndex.from_documents()`** embeds and stores Nodes,
  costing one embedding call per Node (Lesson 4).
- **`as_query_engine()` / `.query()`** run retrieve -> synthesize in
  one call and return a `Response` with `.response` and
  `.source_nodes` (Lesson 5).
- **`as_retriever()` / `.retrieve()`** isolate retrieval alone, no LLM
  call, useful for debugging what an index actually finds (Lesson 6).
- **`response_mode`** (`refine`, `compact`, `tree_summarize`) controls
  how retrieved Nodes get synthesized into one answer (Lesson 7).
- **`as_chat_engine()` / `.chat()`** add conversation memory on top of
  the same pipeline, so follow-up questions work (Lesson 8).

From here, the course's next tier builds on this same foundation:
persisting indexes so you don't re-embed on every run, agents and
tool-calling, and more advanced retrieval and indexing strategies.

If anything here still feels unclear, ask before moving on to the next
tier of this course.
