# Lesson 17 (Checkpoint): An agent that searches a site and reports back

## What this checkpoint proves

This tier started with waiting strategies and ended with a model that
can browse the web on its own. This checkpoint pulls every idea
together into the shape a real agent actually takes: not one question,
one tool call, one answer (Lesson 16), but a **loop** that keeps
browsing until it has enough to answer, however many pages that takes.

Before starting, it's worth being honest with yourself about Lessons
9 through 16: could you explain auto-wait vs explicit wait, write a
form-filling script from scratch, capture a popup tab, and explain why
`browse()` returns strings instead of raising exceptions? If any of
that feels shaky, this is the moment to go back, not push forward.

## Why one round wasn't enough

In Lesson 16, the model always found what it needed on the very first
page it browsed. Real questions are rarely that convenient. This
lesson's question, find quotes tagged `'love'`, can't be answered from
the front page of quotes.toscrape.com; there's no tag filter visible
there. A capable agent has to recognize that, decide to browse a
different, more specific URL (a tag page), and only then has enough
information to answer. That might take one extra round, or several,
depending on how the model reasons about it.

## The code, piece by piece

```python
def run_agent(question: str, max_rounds: int = 5) -> str:
    messages: list = [HumanMessage(question)]

    for round_number in range(1, max_rounds + 1):
        ai_message = model_with_tools.invoke(messages)
        messages.append(ai_message)

        if not ai_message.tool_calls:
            return ai_message.text

        for call in ai_message.tool_calls:
            result = browse.invoke(call["args"])
            messages.append(ToolMessage(content=result, tool_call_id=call["id"]))
```

This is Lessons 13 and 14's three-round pattern, generalized into a
`for` loop. Instead of hardcoding exactly one "ask, run, respond"
cycle, it repeats the same cycle until one of two things happens:

- `ai_message.tool_calls` is empty, meaning the model decided it has
  enough to answer and returned plain text instead of another
  request. We return that text immediately.
- We run out of rounds (`max_rounds`), and give up gracefully instead
  of looping forever.

Every round, `messages` keeps growing, exactly as it did in Lesson 14:
the original question, every tool request the model has made so far,
and every result, all sent back on each call, since the model has no
memory between `.invoke()` calls.

```python
max_rounds: int = 5
```

Why a limit at all? Nothing guarantees a model eventually stops asking
for tools. A vague question, or a page that never actually contains
the answer, could keep it requesting "just one more page" indefinitely.
Bounding the loop is a small guardrail that turns "hangs forever" into
"fails with a clear message," which matters far more once an agent
like this is running unattended rather than watched in a terminal.

## The question this lesson asks

```python
question = (
    "On https://quotes.toscrape.com/, find two quotes tagged 'love' "
    "(hint: tag pages live at https://quotes.toscrape.com/tag/love/). "
    "Report each quote's text and its author."
)
```

The hint about the tag page URL pattern is deliberate scaffolding, not
cheating: real agents are often given hints about how a site is
structured, the same way a human researcher might be told "check the
site's tag pages." What the model still has to do on its own is
recognize it needs a second page at all, decide to call `browse` again
with that URL, and read the result to actually extract the quotes.

## Running it

```bash
uv run python lessons/playwright/02_intermediate/17_intermediate_checkpoint_project/lesson.py
```

Try changing the question, ask for a different tag, or for quotes by a
specific author, and watch how many rounds it takes the model to find
its way there.

## Expected output

```
Question: On https://quotes.toscrape.com/, find two quotes tagged 'love' (hint:
tag pages live at https://quotes.toscrape.com/tag/love/). Report each quote's
text and its author.

Round 1: model requested 1 browse call(s)
  -> browse('https://quotes.toscrape.com/tag/love/')
(answered after 2 round(s))

Final answer:
1. "This life is what you make it. No matter what, you're going to mess up
sometimes..." - Marilyn Monroe
2. "You've gotta dance like there's nobody watching..." - William W. Purkey
```

The exact quotes and round count may vary depending on how the model
reasons about the task.

## Checkpoint

- **The agent loop**: `ask -> if tool requested, run it and report back
  -> ask again`, repeated until the model answers in plain text
  instead of requesting a tool.
- **Why more than one round is often needed**: a single page frequently
  doesn't contain the answer; a capable agent has to decide, on its
  own, to browse somewhere else before it has enough information.
- **`max_rounds` as a guardrail**: nothing guarantees a model stops
  asking for tools on its own; a hard limit turns an infinite loop into
  a clear, recoverable failure.
- **`messages` keeps growing every round**: the model has no memory
  between `.invoke()` calls, the entire conversation so far has to be
  resent every time.

This closes the intermediate tier. If anything from Lessons 9 through
17 still feels unclear, go back and revisit it before starting the
advanced tier, [Lesson 18](../../03_advanced/18_authentication_and_storage_state/).
