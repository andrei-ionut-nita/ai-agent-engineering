# Lesson 11: init_chat_model, choosing a provider with a string

## Revisiting "why LangChain" from Lesson 1

Back in Lesson 1, we said LangChain's whole point is giving you a shared
interface across different AI providers, so switching providers later
means changing a line or two, not rewriting everything. Every lesson
since then has still done one thing the "provider-specific" way:

```python
from langchain_google_genai import ChatGoogleGenerativeAI
model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
```

That `import` line is still tied to Google specifically. If you wanted
to switch to a different provider, you'd need to change the import, not
just a string.

## `init_chat_model`: pick the provider with a string instead

```python
from langchain.chat_models import init_chat_model
model = init_chat_model("google_genai:gemini-3.5-flash-lite")
```

No provider-specific import at all. The string
`"google_genai:gemini-3.5-flash-lite"` has two parts, separated by a
colon: `google_genai` (which integration to use) and
`gemini-3.5-flash-lite` (which model, within that integration). Change
the part before the colon (say, to `anthropic` or `openai`, assuming the
matching package is installed) and you'd get a model from an entirely
different company, with the exact same `.invoke()` interface, no other
code changes needed.

## What's actually happening underneath

```python
print(type(direct_model) is type(agnostic_model))  # True
```

This is worth sitting with: `init_chat_model` isn't some new, different
kind of object. Run the lesson and you'll see both `direct_model` and
`agnostic_model` are the exact same class, `ChatGoogleGenerativeAI`,
underneath. `init_chat_model` didn't invent anything new, it just read
the `"google_genai:"` prefix, figured out that means "build a
`ChatGoogleGenerativeAI`", and built one for you, exactly as if you'd
imported and constructed it yourself.

## Why bother, if it builds the same thing?

The value isn't in this one lesson, where we only ever use Google
anyway. It shows up when:

- You want to let users (or a config file) choose which AI provider to
  use, without your code needing an `if/elif` chain of different
  imports for every possible provider.
- You're comparing multiple providers side by side, and want to swap
  between them by changing one string, not restructuring imports.
- You're writing example code or a tutorial (like this one) meant to
  generalize beyond one specific provider.

## Running it

```bash
uv run python lessons/langchain/01_beginner/11_provider_agnostic_models/lesson.py
```

## Checkpoint

- **`init_chat_model`**: builds a chat model from a
  `"provider:model_name"` string, instead of a provider-specific import.
- **same underlying class**: it doesn't create a new kind of object, it
  builds the exact same class you'd get from importing it directly.
- **when this matters**: letting the provider be chosen dynamically
  (by a user, a config file, or for easy comparison), rather than fixed
  in your imports.

If anything here still feels unclear, ask before moving to Lesson 12,
the Beginner tier's checkpoint project.
