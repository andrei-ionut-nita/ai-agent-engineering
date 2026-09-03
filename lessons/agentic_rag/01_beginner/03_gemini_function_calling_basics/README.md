# Lesson 3: Gemini Function Calling Basics

## Where we left off

Lesson 2 established the problem: a fixed pipeline can't ask "do I
need to retrieve for this?" Function calling is the mechanism that
lets the model ask that question, and any other "should I use a tool"
question, for itself. This lesson introduces the raw mechanics with the
simplest possible example, a fake weather lookup, before Lesson 4
points the same mechanism at retrieval specifically.

This is the one genuinely new API surface this course introduces. The
shapes below (`types.Tool`, `types.FunctionDeclaration`,
`types.Schema`, `response.function_calls`) were confirmed against the
`google-genai` version actually installed in this repo's `.venv`
(`google/genai/types.py`), not assumed from memory or older docs.

## The misconception this lesson corrects

It's easy to assume "function calling" means the model runs the
function. **It doesn't, and it can't.** Gemini has no code execution
environment; it can only *propose* a call, a function name and a
dictionary of arguments, as structured output instead of prose. Nothing
executes until *your own code* reads that proposal and decides to run
the real Python function it names. Gemini requesting `get_current_temperature(city="Lisbon")`
does not mean any HTTP request has happened, it means the model, given
a description of a function, judged that calling it would help answer
the question, and is waiting for your code to act on that judgment or
ignore it entirely.

## The code, piece by piece

```python
GET_TEMPERATURE_DECLARATION = types.FunctionDeclaration(
    name="get_current_temperature",
    description="Get the current outdoor temperature for a named city.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={"city": types.Schema(type=types.Type.STRING, description="...")},
        required=["city"],
    ),
)
```

A `FunctionDeclaration` is a JSON-Schema-shaped description of a
function: its `name` (what the model will ask for by), a `description`
(the single biggest lever over whether and when the model decides to
call it, worded for the model, not for you), and `parameters` (an
OpenAPI-style `Schema` describing each argument's type, description,
and whether it's `required`). Nothing here references a real Python
function, this is purely a description the model reads.

```python
WEATHER_TOOL = types.Tool(function_declarations=[GET_TEMPERATURE_DECLARATION])

response = client.models.generate_content(
    model=CHAT_MODEL,
    contents=question,
    config=types.GenerateContentConfig(tools=[WEATHER_TOOL]),
)
```

A `Tool` bundles one or more declarations (this lesson uses one), and
gets passed through `GenerateContentConfig(tools=[...])`, the same
`config=` parameter every course in this series has already used for
things like `output_dimensionality`. This is the entire API surface
needed to make tools available to the model, nothing about how
`generate_content` itself is called changes.

```python
calls = response.function_calls
```

`response.function_calls` is a convenience property (defined on the
SDK's response type) that pulls out any function-call requests Gemini
made, `None` if it answered directly instead. Each entry is a
`FunctionCall` with `.name` and `.args`, exactly the name and arguments
your own code needs to actually run the function, next lesson's job.

## Running it

```bash
uv run python lessons/agentic_rag/01_beginner/03_gemini_function_calling_basics/lesson.py
```

## Expected output

```
Q: What's the temperature in Lisbon right now?

Gemini did NOT answer directly. It requested a tool call instead:
  name: get_current_temperature
  args: {'city': 'Lisbon'}
```

Occasionally Gemini answers directly with a caveat instead of
requesting the tool (small models are inconsistent about this); if that
happens, the "Gemini answered directly" branch prints instead, itself a
preview of Lesson 6.

## Checkpoint

- **`types.FunctionDeclaration`**: a schema description of a function,
  read by the model, not connected to any real code.
- **`types.Tool(function_declarations=[...])`**: bundles declarations,
  passed via `GenerateContentConfig(tools=[...])`.
- **`response.function_calls`**: `None` or a list of `FunctionCall`
  objects (`.name`, `.args`), Gemini's structured request to call a
  function, never an executed call.
- The model choosing to request a call, versus answering directly, is
  exactly the decision this whole course is about, Lesson 3 is where
  that decision first becomes visible in code.

If anything here still feels unclear, ask before moving to Lesson 4.
