# Lesson 24 (Capstone): An end-to-end web research agent

## What this capstone pulls together

This is the last lesson of the Playwright course, and it doesn't
introduce a new Playwright concept, it combines the ones already
covered into one real agent:

- **Lessons 15-16**: a plain `browse(url)` function, wrapped with
  `@tool` and bound to a Gemini model via `.bind_tools()`.
- **Lesson 14**: the ask/run/respond loop, extended here from three
  fixed steps into a real loop the model controls.
- **Lesson 23**: an allowlist of trusted domains, so the model can never
  navigate anywhere outside `books.toscrape.com` and
  `quotes.toscrape.com`.

The result is a small agent that takes a natural-language research
question, decides for itself what to look up, browses real pages to
find the answer, and reports back, citing what it read.

## Requires GOOGLE_API_KEY

This is the first lesson since Lesson 16 to need a real model call.
Make sure a `.env` file exists at the project root with:

```
GOOGLE_API_KEY=your-key-here
```

## The safety boundary: a domain allowlist

```python
ALLOWED_DOMAINS = {"books.toscrape.com", "quotes.toscrape.com"}

def _domain_is_allowed(url: str) -> bool:
    host = urlparse(url).netloc
    return host in ALLOWED_DOMAINS
```

`urlparse(url).netloc` pulls just the host out of a URL, e.g.
`"books.toscrape.com"` out of
`"https://books.toscrape.com/catalogue/"`. Checking that against a
fixed set is the same pattern Lesson 23 taught: never trust an AI (or
untrusted input generally) to only go where you'd want it to, enforce
the boundary in code. If the model tries to browse anywhere else,
`browse()` refuses and says so, it never even launches a browser for a
disallowed URL.

## The tool itself

```python
@tool
def browse(url: str) -> str:
    """Fetch a page and return its visible text. Only works for URLs on
    books.toscrape.com or quotes.toscrape.com..."""
    if not _domain_is_allowed(url):
        return f"Refused: {url!r} is outside the allowed domains..."

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, timeout=15000)
        page.wait_for_load_state("networkidle")
        text = page.locator("body").text_content() or ""
        browser.close()

    cleaned = " ".join(text.split())
    return cleaned[:MAX_PAGE_TEXT_CHARS]
```

Same idea as Lesson 15's `browse(url)`: a plain Python function that
happens to use Playwright internally, with a docstring written for the
model, not for a human reading the source. `" ".join(text.split())`
collapses all the whitespace, newlines, and indentation a real page's
text carries, into single spaces, so the model spends its context
budget on actual words, not formatting. `[:MAX_PAGE_TEXT_CHARS]` caps
the length for the same reason.

## The research loop

```python
def run_research_agent(model_with_tools, question: str) -> str:
    messages = [SystemMessage(SYSTEM_PROMPT), HumanMessage(question)]

    for turn in range(1, MAX_AGENT_TURNS + 1):
        response = model_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return response.text

        for call in response.tool_calls:
            result = browse.invoke(call["args"])
            messages.append(ToolMessage(content=result, tool_call_id=call["id"]))

    return "Ran out of turns before reaching a final answer, try a narrower question."
```

Lesson 14 walked through three fixed rounds: ask, run the tool, get a
final answer. Here the loop keeps going, up to `MAX_AGENT_TURNS`, as
long as the model keeps asking to browse. The model decides for itself
when it has enough information: the moment a response comes back with
no `tool_calls`, that response is treated as the final answer. The cap
exists purely as a safety net, without one, a model that gets confused
could ask to browse forever, and this course's principle from Lesson
14 still holds: **the AI decides, your code executes**, and your code
also decides when to stop giving it more turns.

## The system prompt

```python
SYSTEM_PROMPT = """You are a careful web research assistant. You can \
only browse books.toscrape.com and quotes.toscrape.com, using the \
browse tool. Use it to look up real information before answering, \
don't guess. ..."""
```

Telling the model about its own restriction, in addition to enforcing
it in code, matters for a subtle reason: a model that knows it's
restricted to two sites won't waste a turn trying (and getting refused)
elsewhere, it'll go straight to a URL it can actually use. The code-level
check in `_domain_is_allowed` is the real safety boundary though, the
system prompt is guidance, not enforcement, exactly the distinction
Lesson 23 draws between trusting instructions and enforcing rules.

## Running it

```bash
uv run python lessons/playwright/03_advanced/24_advanced_capstone_project/lesson.py
```

## Expected output

```
Q: What is the cheapest book listed on the books.toscrape.com homepage?
  [turn 1] browsing: https://books.toscrape.com/
A: Based on the books listed on the homepage (page 1) of books.toscrape.com, the cheapest book is **Starving Hearts (Triangular Trade Trilogy, #1)** at **£13.99**.

Q: Who is quoted first on quotes.toscrape.com, and what is the quote?
  [turn 1] browsing: https://quotes.toscrape.com/
A: Based on quotes.toscrape.com, the first person quoted is **Albert Einstein**, and the quote is:

> "The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking."
```

The exact wording of the model's answers can vary between runs, models
aren't deterministic, but the facts (cheapest price, first quote's
author) should stay consistent, since they're being read off a real,
stable page rather than guessed.

## Where to go from here

This course covered a browser as a tool an agent can use safely and
deliberately: launching it, waiting for real content, filling in forms,
reading structured data, authenticating once and reusing that session,
intercepting network traffic, running many isolated contexts, retrying
through real flakiness, running headless in a container, and treating
page content as untrusted input rather than instructions. A production
browsing agent would add more: better error handling for pages that
never load, structured output instead of free text, and probably a
much larger domain allowlist, but every idea it would build on is
already here.

This is the final lesson of the Playwright course.
