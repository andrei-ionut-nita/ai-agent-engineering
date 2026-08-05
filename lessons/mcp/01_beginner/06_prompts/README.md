# Lesson 6: Prompts, reusable interaction templates

## The third primitive

Tools do things, resources hold data, and **prompts** are the third
piece: reusable, parameterized templates that kick off a particular
kind of interaction. Think of them as a server-hosted version of the
few-shot / templated prompts from `langchain/03_prompt_templates`, just
discoverable and fillable by a client instead of hardcoded into your
own script.

```python
@mcp.prompt()
def code_review(language: str, code: str) -> str:
    """Ask for a structured code review of a snippet."""
    return (
        f"Please review this {language} code for bugs, style issues, "
        f"and possible improvements:\n\n{code}"
    )
```

## Discovering and filling in a prompt

Same list/get shape again:

- `prompts/list` (`await mcp.list_prompts()`): what prompt templates
  exist?
- `prompts/get` (`await mcp.get_prompt(name, arguments)`): fill in this
  template's blanks and hand back the resulting message(s).

```python
prompts = await mcp.list_prompts()
# [Prompt(name='code_review', description='Ask for a structured code review of a snippet.', ...)]

result = await mcp.get_prompt("code_review", {"language": "python", "code": "print(1)"})
# result.messages -> [PromptMessage(role='user', content=TextContent(text='Please review...'))]
```

Notice the return shape: a *list of messages*, not a single string.
A prompt template can hand back a whole conversation starter, a system
message plus an example user turn, not just one line of text.

## Why a server would bother with this

A server author who knows their domain well, say, a code-review tool
provider, can ship the *right way to ask* for a review alongside the
tool that performs one. A host application can surface these as
"slash commands" or a menu a user picks from, rather than the user
needing to know how to phrase the request themselves. This is the same
motivation as `langchain/05_few_shot_prompting`: a well-designed prompt
gets better results than an ad hoc one, and here that expertise ships
with the server instead of living in your own codebase.

## Running it

```bash
uv run python lessons/mcp/01_beginner/06_prompts/lesson.py
```

## Checkpoint

- **`@mcp.prompt()`**: registers a reusable, parameterized interaction
  template.
- **`prompts/list` / `prompts/get`**: discovery and retrieval, filling
  in a template's arguments.
- A prompt returns a *list of messages*, not just a string, letting a
  server hand back a whole conversation starter.
- Prompts let a server ship domain expertise about *how* to ask,
  alongside the tools that do the work.

If anything here still feels unclear, ask before moving to Lesson 7,
handling a tool that fails.
