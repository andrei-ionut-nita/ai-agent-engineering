# Lesson 35: Advanced Capstone - Local Research Assistant Agent

## What this is

No new concepts. This is the final checkpoint of the entire course: a
single agent combining every major idea from the Advanced tier (and,
underneath, everything from Beginner and Intermediate too). If you can
read `lesson.py` and understand why every piece is there, you've
completed this course's full arc, from a single `.invoke()` call in
Lesson 1 to a real, multi-capability agent here.

## What it does

A command-line research assistant with:

- A calculator tool (Lessons 13-14)
- RAG search over local notes (Lessons 27-29)
- Real memory across turns via a checkpointer (Lessons 23-24)
- Automatic conversation summarization once a session gets long (Lessons
  25-26)
- A human approval gate before an irreversible action (Lesson 30)
- Basic tracing of every tool call (Lesson 34)

## Where each piece came from

```python
@tool
def calculator(...): ...
@tool
def search_personal_notes(...): ...
```
Lessons 13-15 (tool definitions, multiple tools) and 27-29 (loading and
splitting `notes.txt`, embedding it into an `InMemoryVectorStore`,
wrapping similarity search as a tool).

```python
summarizer = SummarizationMiddleware(model=model, trigger=("messages", 12), keep=("messages", 4))
```
Lessons 25-26's concept (keep old information around in compressed
form instead of dropping it), now using LangChain's actual built-in
middleware for it, instead of the hand-rolled version from Lesson 26.
Once the conversation passes 12 messages, older ones get automatically
compressed into a summary, keeping the most recent 4 in full.

```python
agent = create_agent(
    model=model,
    tools=[calculator, search_personal_notes, delete_note_section],
    middleware=[summarizer],
    checkpointer=InMemorySaver(),
    interrupt_before=["tools"],
)
```
Lessons 23-24 (`create_agent`, `InMemorySaver`, `thread_id` memory) and
30 (`interrupt_before`, pausing before any tool runs).

## The selective approval gate: new here, built from familiar pieces

```python
RISKY_TOOLS = {"delete_note_section"}
...
risky_calls = [c for c in last_message.tool_calls if c["name"] in RISKY_TOOLS]
if risky_calls:
    answer = input("  Approve this action? (yes/no): ").strip().lower()
    if answer not in {"yes", "y"}:
        print("  Rejected, action was not performed.\n")
        return
final = agent.invoke(None, {**config, "callbacks": [tracer]})
```

Lesson 30's `interrupt_before=["tools"]` pauses before *every* tool
call, unconditionally, there's no built-in way to say "only pause for
this specific tool" at that level.

This capstone adds that selectivity in plain Python: after the agent
pauses, we check whether the requested tool's name is in `RISKY_TOOLS`.
If it's not (like `calculator` or `search_personal_notes`), we resume
immediately, no prompt, the user never notices a pause happened. If it
is (`delete_note_section`), we actually ask before resuming. Same
underlying mechanism as Lesson 30, now applied selectively instead of
to every tool call uniformly.

## Basic tracing, kept lightweight

```python
class BasicTracer(BaseCallbackHandler):
    def on_tool_start(self, serialized, input_str, **kwargs) -> None:
        print(f"  [trace] tool call: {serialized.get('name')}({input_str})")
```

A stripped-down version of Lesson 34's `TracingHandler`, just enough to
see which tool ran with what arguments, on every turn, without the full
timing instrumentation. Real applications tune how much tracing detail
they need; this capstone shows the minimum useful amount.

## Running it

```bash
uv run python lessons/langchain/03_advanced/35_advanced_capstone_project/lesson.py
```

Try a conversation like:

```
You: What is 45 times 12?
  [trace] tool call: calculator({'expression': '45 * 12'})
Agent: 45 times 12 is 540.

You: What do my notes say about my garden?
  [trace] tool call: search_personal_notes({'query': 'garden'})
Agent: According to your notes, the garden has three raised beds...

You: delete the pizza recipe notes
  [approval needed] delete_note_section({'topic': 'pizza recipe'})
  Approve this action? (yes/no): yes
  [trace] tool call: delete_note_section({'topic': 'pizza recipe'})
Agent: I have permanently deleted the notes section about the pizza recipe.
```

Try rejecting a risky request too (answer "no"), and confirm the tool
never actually runs.

## Where to go from here

This course covered the full path from a single `.invoke()` call to a
production-shaped agent: message types, templates, chains, tools,
memory, structured output, streaming, context management, RAG,
human-in-the-loop, multi-agent delegation, persistence, middleware, and
tracing.

From here, natural next steps (beyond this course) include: trying a
persistent checkpointer (Lesson 32) in this capstone instead of
`InMemorySaver`, adding a real web-search tool instead of local notes,
or exploring LangGraph directly for agents with custom, non-linear
control flow beyond what `create_agent`'s default loop provides.

Congratulations on completing the course.
