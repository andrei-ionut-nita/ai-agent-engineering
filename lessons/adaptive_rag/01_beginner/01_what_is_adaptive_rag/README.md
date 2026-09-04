# Lesson 1: What Is Adaptive RAG, and Why Route at All?

## Where we left off

If you've completed `naive_rag`, `hybrid_rag`, `graph_rag`,
`corrective_rag`, and `agentic_rag`, you've built five different ways of
turning a question into a grounded answer, and watched each one fail in
its own specific way. Every one of those courses still made a choice
before you ever asked it a question: which retrieval strategy to run,
fixed, for every question that strategy's lesson threw at it. That was
the right call for teaching each strategy in isolation. It stops being
the right call the moment two different questions, asked back to back,
need two different strategies to answer well.

**Adaptive RAG** is the idea that a system should look at a question
first, decide what kind of question it is, and only then pick how to
retrieve for it. Not every question needs the same retrieval strategy: a
one-fact lookup and a question whose answer is scattered across two
documents are not the same problem, and running both through the same
fixed pipeline treats them as if they were.

## A multi-hop question, against a fixed single-document strategy

This lesson reuses `naive_rag`'s own Lesson 8 pipeline, chunk, embed,
retrieve top-1, generate, unchanged, and asks it a question this
course's fixtures were built to expose: "What two hobbies happen in the
same room as the weather station?"

The answer needs two files at once. `bookshelf.md` says the study has a
bookshelf (one hobby: organizing it) and that the weather station's
Raspberry Pi lives there too. `cello-practice.md` independently confirms
the same room and names the other hobby: cello practice. Neither file
alone names both hobbies, only together do they answer the question
fully.

Top-1 retrieval, by definition, hands the model exactly one of those two
files. Whichever one scores higher this run, the model can only answer
with what that single file says, or, just as likely, conclude the
context doesn't mention any hobbies at all, because the file it got
doesn't actually say "hobby" anywhere in those words. Either outcome is
the same underlying problem: a fixed k=1 naive strategy structurally
cannot see two documents at once, no matter how the prompt is worded.

## The code, piece by piece

This lesson's `lesson.py` is `naive_rag` Lesson 8's `retrieve()` and
`generate_answer()`, byte-for-byte the same shape, run once against a
question chosen specifically because that shape can't answer it well.
Nothing here is new mechanically; what's new is diagnosing *why* it
comes up short, and naming that as a routing problem rather than a
retrieval-quality problem. The chunking, embedding, and generation code
already works correctly, individually. The failure is entirely in
`k=1` being the wrong shape for this question.

## Running it

```bash
uv run python lessons/adaptive_rag/01_beginner/01_what_is_adaptive_rag/lesson.py
```

## Expected output

```
Question: What two hobbies happen in the same room as the weather station?

Naive top-1 retrieval picked: <bookshelf.md or cello-practice.md> (score=0.xxxx)

Answer from one document alone:
<names at most one hobby, or admits the context doesn't mention hobbies>
```

followed by this course's four-step roadmap. Gemini's exact wording
varies each run, and which file scores higher can also vary, but the
answer should never correctly name both hobbies, since only one file
ever reaches the model.

## Checkpoint

- **Adaptive RAG**: classify a question's complexity, then route it to
  the retrieval strategy suited to that complexity, instead of running
  every question through the same fixed pipeline.
- A fixed strategy isn't "broken," it's simply the wrong shape for some
  questions: naive top-1 retrieval is genuinely good at single-fact
  lookups (the rest of this series proved that), and genuinely bad at
  anything needing more than one document at once.
- This course's roadmap: classify, route, retrieve (with whichever
  strategy fits), generate. Lessons 3 through 8 build exactly that, one
  piece at a time.

If anything here still feels unclear, ask before moving to Lesson 2.
