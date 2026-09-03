# Lesson 3: Extracting Entities From Text by Hand

## Where we left off

Lessons 1 and 2 established the problem: a multi-hop question needs
facts connected across documents, and similarity search can't find that
connection on its own. Building a knowledge graph starts with the same
first step humans use when reading a document and mentally noting "who
and what is this about": pulling out the **entities**, the people,
places, and things a document talks about.

## Why prompt Gemini for this instead of writing a parser

You might assume this needs proper NLP tooling, a named-entity-
recognition model, part-of-speech tagging, something specialized. It
doesn't, not at this scale. A general-purpose language model like
Gemini is already extremely good at "read this paragraph, tell me who
and what it's about," because that's a language-understanding task, not
a specialized statistical one. Asking a general model to do this well
just requires being specific about the *shape* of the answer you want
back, which is what the prompt below does.

## The code, piece by piece

```python
prompt = f"""List the named entities (people, places, and things - not
generic nouns) mentioned in the text below. Return them as a JSON array
of short strings, using each entity's most natural full name...

Text:
{text}"""

response = client.models.generate_content(
    model=CHAT_MODEL,
    contents=prompt,
    config=types.GenerateContentConfig(response_mime_type="application/json"),
)
entities = json.loads(response.text)
```

Two things matter here. First, the prompt explicitly excludes "generic
nouns": without that instruction, a model will happily list "sensor,"
"garage," and "readings" as entities, which are real words but not the
kind of thing you'd draw an edge to or from in a graph, they're
categories, not identifiable things. Second,
`response_mime_type="application/json"` isn't a formatting nicety, it's
what makes this reliable: instead of hoping Gemini's free-text response
happens to be parseable, this setting constrains the model to emit valid
JSON, which `json.loads` can then turn straight into a Python list, no
regex or string-splitting involved.

## Running it

```bash
uv run python lessons/graph_rag/01_beginner/03_extracting_entities_by_hand/lesson.py
```

## Expected output

```
--- greenhouse.md ---
['Dev', 'greenhouse', 'peppers', 'humidity sensor']

--- maintenance-log.md ---
['Mia', 'greenhouse', 'humidity sensor', 'multimeter', 'garage bench', 'smoke detectors', 'gutter downspout']
```

Exact entity lists vary slightly run to run (a model might say "the
humidity sensor" one time and "humidity sensor" the next), which is
itself worth noticing: extraction isn't perfectly deterministic, a
theme this course returns to directly in Lesson 11 (normalizing
mentions that don't match exactly) and Lesson 16 (what happens when
extraction gets something wrong).

## Checkpoint

- **Entity extraction**: pulling named, identifiable things (not generic
  categories) out of unstructured text, the first step toward a graph.
- A general-purpose language model can do this well with a specific
  enough prompt, no specialized NER tooling required at this scale.
- `response_mime_type="application/json"` constrains the model's output
  format directly, turning "hopefully parseable text" into "guaranteed
  valid JSON."
- Extraction is not perfectly consistent between runs. Keep that in mind
  starting now, it becomes the central problem of the Intermediate tier.

**Try this yourself:** run this lesson against `book-club.md` (edit
`SOURCE_FILE` at the top of `lesson.py`) and predict the entity list
before running it. Does Gemini include "The Overstory" as an entity? Does
it include "heat-shrink tubing"? Neither answer is wrong, both are
defensible calls a human extracting entities by hand could also make
differently, which is worth sitting with before Lesson 4.

If anything here still feels unclear, ask before moving to Lesson 4.
