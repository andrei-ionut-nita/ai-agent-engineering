# Lesson 23: Swapping a LlamaIndex Query Engine Into LangGraph

## Frameworks aren't mutually exclusive

Lesson 1 named the two courses' different centers of gravity: LangChain
is chain-centric, LlamaIndex is data-centric. In production those
aren't competing choices, you use each for what it's best at. This
lesson demonstrates that directly: a `QueryEngine`, built entirely with
LlamaIndex's own vocabulary and RAG machinery (the best tool for "answer
questions about a pile of documents"), gets wrapped as a plain tool
function and handed to a LangChain/LangGraph agent (the best tool for
"reason step by step and decide which of several actions to take").

This mirrors two lessons you've already seen: `lessons/ollama/02_intermediate/13_swapping_into_langchain`
(dropping one framework's model into another with minimal glue code) and
`lessons/langchain/03_advanced/29_rag_as_a_tool` (wrapping retrieval as
a `@tool` an agent decides, on its own, whether to call). This lesson
combines both ideas, but the retrieval side is now LlamaIndex's, not
LangChain's own vector store.

## The boundary is one plain function

```python
@tool
def search_nimbus_policies(question: str) -> str:
    """..."""
    response = query_engine.query(question)
    return str(response.response)
```

Everything LlamaIndex does internally, embedding the question, retrieving
Nodes, synthesizing an answer, stays entirely inside `query_engine.query()`.
LangChain's agent never sees a `VectorStoreIndex`, a `Node`, or
`Settings`, it sees a plain Python function that takes a string question
and returns a string answer. This is the entire integration surface, one
function call.

## Two separate model objects, on purpose

```python
Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)      # LlamaIndex
agent_model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")             # LangChain
```

`Settings.llm` (LlamaIndex's `GoogleGenAI`) powers the query engine's
retrieval and synthesis. `agent_model` (LangChain's
`ChatGoogleGenerativeAI`) powers the outer agent's reasoning about which
tool to call and how to phrase the final answer. Both point at the same
underlying Gemini model and API key, but they are two separate Python
objects, each configured the normal way for its own framework. Nothing
is shared between them except the `search_nimbus_policies` function's
input and output strings, and that's exactly what makes this pattern
composable: either framework's internals can change independently
without breaking the other side.

## Why reach for this instead of picking one framework

If your whole application is "answer questions about documents,"
LlamaIndex alone (Lessons 1-22) is simpler, and you'd never wrap it in
anything. This pattern earns its place once the application is bigger
than that, an agent that also books meetings, searches the web, calls
internal APIs, and needs document search as just one capability among
several. LangGraph's (or Pydantic AI's) job is orchestrating that larger
decision loop; LlamaIndex's job stays exactly what it's always been:
being very good at RAG over your documents.

## The code, piece by piece

```python
agent = create_agent(
    model=agent_model,
    tools=[search_nimbus_policies],
    system_prompt="...",
)
```

Identical shape to Lesson 29 in the langchain course, `create_agent`
doesn't know or care that one of its tools happens to be backed by a
different RAG framework underneath, a tool is a tool.

```python
result = agent.invoke({"messages": [HumanMessage(question)]})
```

Same invocation pattern as every LangChain/LangGraph agent lesson in
this repo, the LlamaIndex-backed tool participates in the normal
tool-calling loop exactly like any other `@tool`.

## Pydantic AI would work the same way

This lesson picked LangGraph (via `create_agent`) because it already
matches this repo's established "swap into another framework" and
"RAG as a tool" conventions. Pydantic AI's version of the same idea
would look like:

```python
from pydantic_ai import Agent

pydantic_agent = Agent(model="google-gla:gemini-3.5-flash-lite")

@pydantic_agent.tool_plain
def search_nimbus_policies(question: str) -> str:
    response = query_engine.query(question)
    return str(response.response)
```

Same body, same one-line call into the LlamaIndex query engine, just a
different decorator on a different agent object. The integration point,
a plain function wrapping `query_engine.query()`, doesn't change based
on which outer framework calls it.

## Running it

```bash
uv run python lessons/llamaindex/03_advanced/23_swapping_into_langgraph_and_pydantic_ai/lesson.py
```

## Expected output

The agent's exact wording varies between runs (both the tool-calling
decision and the final phrasing are LLM outputs), captured from a real
run below; the notice period and "Paris" facts should be stable:

```
Q: How much notice do I need to give before taking vacation at Nimbus Robotics?
A: For vacations longer than two consecutive days, you must submit a request through the HR portal at least **five business days** in advance.

Q: What is the capital of France?
A: The capital of France is Paris.

The same pattern applies to Pydantic AI: instead of @tool + create_agent, you'd decorate a function with @agent.tool on a pydantic_ai.Agent, and its body would still be exactly one line, query_engine.query(...). Either framework works as the 'outer' agent; only the tool-registration syntax changes, the LlamaIndex query engine underneath is untouched.
```

## Checkpoint

- **The integration surface is one plain function**: a LlamaIndex
  `QueryEngine` wrapped in a `@tool`-decorated function that calls
  `query_engine.query()` and returns a string, nothing LlamaIndex-specific
  crosses into the outer agent framework.
- Two separate model objects, one per framework (`Settings.llm` for
  LlamaIndex, a LangChain chat model for the agent), even when they
  point at the same underlying provider and model name.
- `create_agent` and LlamaIndex's `QueryEngine` compose without either
  needing to know the other exists, this is what "frameworks aren't
  mutually exclusive" looks like in real code.
- The same wrapping pattern applies to Pydantic AI (`@agent.tool_plain`
  instead of `@tool` + `create_agent`), only the outer decorator changes.

If anything here still feels unclear, ask before moving to Lesson 24.
