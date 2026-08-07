# Lesson 16: Wiring it into LangChain

## Where we left off

Lesson 15 built `browse(url)` as a plain function and proved it works
entirely on its own, no AI involved. This lesson takes that exact same
function, adds `@tool`, and hands it to a Gemini model, following the
same pattern as Lessons 13 and 14 of the langchain course: build the
tool plainly first, then connect it.

This lesson needs a `GOOGLE_API_KEY` in `.env` at the project root
(see [Setup in the root README](../../../../README.md#setup)); it's
the first lesson in this course that makes a real call to an LLM.

## The code, piece by piece

```python
@tool
def browse(url: str) -> str:
    """Open a URL in a browser and return its visible, readable page text."""
    ...
```

The body of `browse` is unchanged from Lesson 15, character for
character. `@tool` only adds metadata around it: a name (`browse`),
a description (this docstring), and an argument schema (`url: str`).
Nothing about how the function itself works had to change to make it
usable by a model, that's what building it plainly first bought us.

```python
model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
model_with_tools = model.bind_tools([browse])
```

Exactly the same call as Lesson 14 of the langchain course, just with
`browse` in place of `calculator`. `bind_tools` describes the tool to
the model, it does not hand the model a real browser. The model can
never open a page itself, it can only ask.

## The three rounds, applied to a browser

**Round 1: ask the question.**

```python
ai_message = model_with_tools.invoke(messages)
```

We ask what the first quote on a specific page is. The model has no
reliable way to know the live content of that page (it wasn't
necessarily part of its training data, and the page could change
anyway), so instead of guessing, it should reply with a request:
"call `browse` with `url='https://quotes.toscrape.com/'`."

**Round 2: we run the browser, and report back.**

```python
for call in ai_message.tool_calls:
    result = browse.invoke(call["args"])
    messages.append(ToolMessage(content=result, tool_call_id=call["id"]))
```

This is the moment a real Chromium instance actually launches, on our
machine, not the model's. The model asked, our code decided to honor
that request and did the work. `browse.invoke(...)` here runs the
exact same `browse` function Lesson 15 tested directly, no difference
at all in how it executes.

**Round 3: let the model read the page and answer.**

```python
final_response = model_with_tools.invoke(messages)
```

We send the full conversation, including the raw page text `browse`
returned, back to the model. It reads through that text and picks out
just the quote and its author, in a normal sentence, instead of us
having to write parsing code to find "the first quote" ourselves.

## Running it

```bash
uv run python lessons/playwright/02_intermediate/16_wiring_it_into_langchain/lesson.py
```

## Expected output

```
Did the model ask to use a tool? True
  -> wants to call browse with {'url': 'https://quotes.toscrape.com/'}

Final answer: The first quote is "The world as we have created it is a process
of our thinking. It cannot be changed without changing our thinking." said by
Albert Einstein.
```

## Checkpoint

- **Same function, no changes**: `@tool` only attaches metadata around
  `browse`, the function body from Lesson 15 stays exactly as it was.
- **The model still can't touch anything directly**: `bind_tools`
  describes the tool, it never gives the model the ability to run
  code, open a browser, or reach the network. Your code still executes
  every request.
- **Why the model needs the tool at all**: live page content isn't
  something a model can reliably know or guess, it has to be fetched
  for real, then handed back for the model to read and summarize.

If anything here still feels unclear, ask before moving to Lesson 17,
this tier's checkpoint project.
