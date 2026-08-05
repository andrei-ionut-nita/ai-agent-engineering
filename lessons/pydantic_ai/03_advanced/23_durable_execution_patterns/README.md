# Lesson 23: Durable execution patterns

## Three separate reliability concerns

"Make this production-ready" usually bundles together three distinct
problems. Pydantic AI gives each one its own, separate mechanism,
rather than one big "be reliable" flag:

1. **Retries for the model's own mistakes**: covered in Lesson 8
   (`ModelRetry` from an output validator) and available per-tool too,
   via `retries=` on `@agent.tool`.
2. **Fallback for a whole provider failing**: covered in Lesson 22
   (`FallbackModel`).
3. **Idempotency for tools with real side effects**: not something
   Pydantic AI does for you, this lesson's actual subject, because
   only you know what "processing the same request twice" means for
   your system.

## Per-tool retries

A tool can have its own retry budget, separate from the agent's
overall `retries`:

```python
@agent.tool(retries=3)
def flaky_lookup(ctx: RunContext[None], query: str) -> str:
    ...
    raise ModelRetry("Lookup timed out, try a narrower query.")
```

Each `ModelRetry` here counts against this tool's 3, not the agent's
global limit, so one unreliable tool doesn't eat into every other
tool's retry budget.

## Idempotency: the pattern this lesson actually builds

If a tool call has a real side effect (charging a card, sending an
email) and a retry, from the model reformulating its approach, from
your own infrastructure retrying a failed request, causes the same
tool to be called again with the same arguments, you don't want the
side effect to happen twice. The standard fix is an idempotency key: a
stable identifier for "this logical operation," checked against a
record of operations already completed, before the side effect runs.

```python
@dataclass
class PaymentDeps:
    processed: set[str] = field(default_factory=set)

@agent.tool
def charge_card(ctx: RunContext[PaymentDeps], idempotency_key: str, amount: float) -> str:
    if idempotency_key in ctx.deps.processed:
        return f"Already processed {idempotency_key}, not charging again."
    ctx.deps.processed.add(idempotency_key)
    return f"Charged ${amount:.2f} (key={idempotency_key})."
```

In a real system, `processed` would be a database table or a Redis
set, something that survives past one Python process, not an in-memory
set. The shape of the check (look up the key, skip if seen, record it
before/while doing the real work) is what matters, and it's identical
whether the storage behind it is a `set()` or Postgres.

## Running it

```bash
uv run python lessons/pydantic_ai/03_advanced/23_durable_execution_patterns/lesson.py
```

## Checkpoint

- Per-tool `retries=` is a separate budget from the agent's overall
  retry limit.
- `FallbackModel` (Lesson 22) and tool retries solve different
  problems: a bad response versus a whole provider being down.
- Idempotency (checking a stable key before a side effect runs) is a
  pattern you build yourself, agent frameworks can't know what "the
  same operation" means for your specific side effect.

If anything here still feels unclear, ask before moving to Lesson 24,
this course's capstone.
