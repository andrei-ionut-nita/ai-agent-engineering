# Lesson 16: Tool error handling, when a tool call goes wrong

## Where we left off

Every tool call in Lessons 14 and 15 succeeded. In the real world, tools
fail: bad input, a network problem, a calculation that's simply
undefined (like dividing by zero). This lesson asks the calculator to
divide by zero on purpose, and compares two ways of handling that.

## The naive version: no error handling

```python
for call in ai_message.tool_calls:
    result = calculator.invoke(call["args"])
    messages.append(ToolMessage(content=result, tool_call_id=call["id"]))
```

If `calculator.invoke(...)` raises an exception, this line crashes
immediately. Not just this one question, the entire program stops,
right there, with a raw Python traceback. Run
`ask_without_error_handling` in this lesson and you'll see exactly that:
a `ZeroDivisionError` bubbling all the way up and killing the script.

## The robust version: catch it, report it, keep going

```python
for call in ai_message.tool_calls:
    try:
        result = calculator.invoke(call["args"])
    except Exception as error:
        result = f"Error: {error}"

    messages.append(ToolMessage(content=result, tool_call_id=call["id"]))
```

Same loop, one addition: a `try`/`except` around the risky line. If the
tool raises, we don't crash, we build a `ToolMessage` describing what
went wrong instead of what the answer was. The model receives that
`ToolMessage` exactly the same way it receives a successful result, it
just contains an error description instead of a number this time. The
model then reacts sensibly (it explains the problem to the user) instead
of the whole program dying.

## Why the model sometimes skips the tool entirely

You might notice, depending on the exact wording of the question, the
model sometimes answers "division by zero is undefined" directly,
without calling the calculator at all, it already knows that fact and
doesn't need a tool to state it. That's why both functions in this
lesson check `if not ai_message.tool_calls` first (same guard from
Lesson 15), and why the question explicitly says "use the calculator
tool", to make sure this lesson's actual point, a tool genuinely
failing, gets exercised.

## A tool error is not a total failure

This is the real idea to take away: catching the exception doesn't mean
pretending nothing went wrong, it means the *failure itself becomes
information the model can use*, rather than a program crash. A tool
that can fail gracefully (reporting "this input caused an error") is far
more useful in a real application than one that takes the whole program
down the first time something unexpected happens.

## Running it

```bash
uv run python lessons/langchain/02_intermediate/16_tool_error_handling/lesson.py
```

You should see the error-handled version explain the problem in plain
language, followed immediately by the naive version crashing with a
`ZeroDivisionError` traceback, same failing input, two very different
outcomes.

## Checkpoint

- **uncaught tool exception**: crashes the entire program, not just that
  one question.
- **`try`/`except` around the tool call**: turns a crash into a
  `ToolMessage` the model can read and react to.
- **a caught error is still useful information**: the model can explain
  a failure sensibly, if it's told about it instead of the program just
  dying.

If anything here still feels unclear, ask before moving to Lesson 17.
