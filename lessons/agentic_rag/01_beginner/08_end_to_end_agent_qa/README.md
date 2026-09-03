# Lesson 8: End-to-End Agent Q&A

## Where we left off

No new mechanism this lesson, `ask()` is Lesson 7's loop, unchanged.
What's new is the test: three questions, one needing retrieval, one
needing the time tool, one needing neither, run through the exact same
function, to see all three decisions the Beginner tier has built land
correctly in a single run.

## The code, piece by piece

The only change from Lesson 7 is `ask()`'s return type, now
`tuple[str, str]`, so `main()` can print which tool (if any) actually
ran alongside each answer:

```python
def ask(query: str, store: list[dict]) -> tuple[str, str]:
    ...
    if not calls:
        return response.text or "", "none"
    ...
    return final_response.text or "", call.name
```

Nothing else moved. This lesson exists to demonstrate a property, not
introduce one: the same unmodified code correctly handles all three
cases because the branching lives inside Gemini's own judgment, not in
this course's `if` statements.

## Why this is the Beginner tier's actual milestone

Compare this to what would be required to get the same three answers
correctly with the fixed pipeline from Lesson 2: you'd need to write
code that first classifies each incoming question as "needs retrieval,"
"needs the time," or "needs neither," *before* deciding what to do,
essentially reimplementing the judgment Gemini's function calling
already gives you as a side effect of asking it a question with tools
declared. That classification step is real engineering work in a fixed
pipeline; here, it's not code at all.

## Running it

```bash
uv run python lessons/agentic_rag/01_beginner/08_end_to_end_agent_qa/lesson.py
```

## Expected output

```
Q (retrieval): How often does Clarence the sourdough starter need feeding at room temperature?
  tool used: search_notes
  A: Clarence needs feeding every 12 hours at room temperature.

Q (the time tool): What time is it right now in Lisbon?
  tool used: get_current_datetime
  A: <the current date and time in Europe/Lisbon>

Q (neither, straight arithmetic): What is 7 times 8?
  tool used: none
  A: 56
```

## Checkpoint

- No new code, `ask()` is Lesson 7's loop, this lesson demonstrates it
  generalizing correctly across three distinct question shapes in one
  run.
- The routing logic ("which tool, if any, does this need") lives
  entirely inside the model's own judgment, not in hand-written
  classification code.
- This is the shape Lesson 9's checkpoint packages into something you'd
  actually hand someone to use.

If anything here still feels unclear, ask before moving to Lesson 9.
