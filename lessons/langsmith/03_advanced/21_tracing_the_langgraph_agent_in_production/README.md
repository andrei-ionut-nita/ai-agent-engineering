# Lesson 21: Tracing a LangGraph agent as if it were running in production

## What we're building

The same calculator/word-counter agent from Lesson 6 (and langgraph
course, lesson 23), handling three simulated requests from two
different users, each request tagged and labeled for production
monitoring, one of them given user feedback afterward, then confirmed
findable via a filtered query.

## What this reveals

langgraph course, lesson 32 (`tracing_and_observability`) covered
watching a graph run step by step, `print()` statements, and
`get_graph()`, useful while developing locally, on your machine, one
run at a time. Production is a different situation entirely: many
concurrent requests, from many different users, that you are not
watching live, and need to be able to inspect *after* the fact, hours or
days later. This lesson combines three tools this course already built,
`config` metadata/tags (Lesson 6), per-request feedback (Lesson 17), and
filtered queries (Lesson 18), into the shape a real production
integration actually takes.

The two pieces of metadata that matter most in practice are exactly the
ones used here: `user_id` (who made this request, so you can look up
"everything this user experienced") and `environment` (so
production traffic never gets confused with your own local testing runs,
Lessons 1-20 in this very course would otherwise show up mixed in
with real usage).

## The code, piece by piece

```python
run_id = str(uuid.uuid4())
result = app.invoke(
    {"messages": [HumanMessage(question)]},
    config={
        "run_name": "production_agent_request",
        "tags": ["langsmith-course", "production"],
        "metadata": {"user_id": user_id, "environment": "production"},
        "run_id": run_id,
    },
)
```

Everything here is a combination of earlier lessons: `tags`/`metadata`
from Lesson 6, and a pre-assigned `run_id` from Lesson 17, passed
through LangGraph's `config` instead of `langsmith_extra` since this is
a LangChain/LangGraph-native call, not a raw `@traceable` function.

```python
client.create_feedback(run_id=run_ids[0], key="user_thumbs_up", score=1)
```

Identical to Lesson 17, just attached to an agent's run instead of a
single traced function's run, feedback doesn't care what kind of run
produced the id.

```python
production_runs = list(client.list_runs(project_name=PROJECT_NAME, filter='has(tags, "production")', limit=10))
```

The same filtered query as Lesson 18, narrowed to the `"production"`
tag specifically, exactly how you'd separate real usage from
development traffic in a shared LangSmith project.

## Running it

```bash
uv run python lessons/langsmith/03_advanced/21_tracing_the_langgraph_agent_in_production/lesson.py
```

In the UI, filter runs by `metadata.user_id = "user-1"` and confirm both
of that user's requests appear, then check the first request's Feedback
panel for `user_thumbs_up`.

## Checkpoint

- **Production observability vs. local debugging**: `print()` and
  `get_graph()` (langgraph lesson 32) help while developing; metadata,
  tags, and feedback (this lesson) help after the fact, at scale, across
  users.
- **`user_id` and `environment` metadata**: the two most practically
  useful labels for separating and attributing production traffic.
- **The same tools, applied to a real agent**: Lessons 6, 17, and 18's
  techniques compose directly onto any LangGraph application, not just
  the single-function examples they were introduced with.

If anything here still feels unclear, ask before moving to Lesson 22.
