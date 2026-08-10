# Lesson 17: Intermediate checkpoint, RAG as a tool

## Checkpoint: putting Lessons 10-16 together

This lesson introduces nothing new. It recombines pieces from across this
tier into one small, working agent, which is the point of a checkpoint,
proving the pieces genuinely compose rather than only working in
isolation:

- **Lesson 4/5's `VectorStoreIndex` + `QueryEngine`**, wrapped as a
  `QueryEngineTool` (Lesson 16's idea, used with one tool here instead of
  two): a query engine is itself just a tool an agent can decide to call,
  "RAG as a tool" rather than RAG as the whole program.
- **Lesson 14's `FunctionTool`**, wrapping a plain Python function, a
  trivial numeric calculation this time instead of a dict lookup.
- **Lesson 15's `FunctionAgent`**, choosing between the two per question.

The agent below has two tools that answer fundamentally different kinds of
questions, one retrieves and synthesizes from real documents, the other
computes an answer with no documents involved at all. Picking the right
one per question is the actual exercise; nothing about the LLM call itself
changes based on which kind of tool gets used.

## The code, piece by piece

```python
def build_policy_tool() -> QueryEngineTool:
    documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    return QueryEngineTool(
        query_engine=query_engine,
        metadata=ToolMetadata(
            name="nimbus_policy_search",
            description=(
                "Answers questions about Nimbus Robotics' written policies: "
                "vacation, remote work, and expense reimbursement. Use this "
                "for anything a policy document would contain."
            ),
        ),
    )
```

Builds one index over all three Nimbus policy files (unlike Lesson 16's
two separate single-document indexes), since this tool needs to answer
whatever policy question comes up, not just one topic, then wraps it as a
`QueryEngineTool` exactly the way Lesson 16 did.

```python
def days_until_review(months_employed: int) -> str:
    """Compute how many days until an employee's next performance review. ..."""
    review_cycle_months = 6
    months_until_next = review_cycle_months - (months_employed % review_cycle_months)
    ...
```

A trivial, deterministic calculation with nothing document-related about
it, on purpose, so the agent's tool choice is a real decision rather than
both tools plausibly answering the same question.

```python
agent = FunctionAgent(
    tools=[policy_tool, review_tool],
    llm=Settings.llm,
    system_prompt=(
        "You are a Nimbus Robotics HR assistant. Use nimbus_policy_search "
        "for questions about written policy, and days_until_review for "
        "questions about when someone's next performance review is. "
        "Keep answers short."
    ),
)
```

Same `FunctionAgent` construction as Lesson 15, just with a
`QueryEngineTool` and a `FunctionTool` mixed in the same `tools` list.
From the agent's perspective both are just `AsyncBaseTool` objects with a
name and a description, it decides which to call by matching the question
against each tool's description, the same mechanism either way.

```python
for question in questions:
    response = await agent.run(user_msg=question)
```

Two independent questions, run one after another (a fresh loop each time,
not a multi-turn conversation), each expected to route to a different
tool: one is answerable only from the policy documents, the other only by
computation.

## Running it

```bash
uv run python lessons/llamaindex/02_intermediate/17_intermediate_checkpoint_project/lesson.py
```

## Expected output

Captured from a real run. Exact phrasing can vary between runs (both
answers involve at least one LLM call), but which tool gets picked for
each question should be stable given these descriptions:

```
Question: How many days of paid parental leave does Nimbus Robotics offer?
Answer: Nimbus Robotics offers 12 weeks of paid parental leave.

Question: An employee has been here 8 months. How long until their next performance review?
Answer: 4 months.
```

## Checkpoint

- **RAG as a tool**: a `QueryEngine` wrapped as a `QueryEngineTool` is
  just another tool from an agent's point of view, retrieval and
  synthesis happen inside the tool call, not as a separate program stage.
- **One `FunctionAgent`, mixed tool types**: a `QueryEngineTool` and a
  `FunctionTool` sit side by side in the same `tools` list, no special
  handling needed for either kind.
- Tool descriptions are what drives correct routing, precise, distinct
  descriptions matter more than anything about the tools' internals.
- This closes the loop from Lesson 1's four-object mental model
  (`Document` -> `Node` -> `Index` -> `QueryEngine`) through Lesson 14's
  single tool call and Lesson 15's agent loop to Lesson 16's multi-source
  routing, all four pieces now live inside one agent.

If anything here still feels unclear, ask before moving to Lesson 18.
