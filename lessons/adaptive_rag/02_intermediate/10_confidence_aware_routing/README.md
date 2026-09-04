# Lesson 10: Confidence-Aware Routing

## Where we left off

Beginner Lessons 3-6 built a classifier that reads a question and
returns exactly one label: `simple_factual`, `multi_hop`, or
`ambiguous`. That label is all the router ever saw, and a label alone
can't distinguish "the classifier is confident" from "the classifier
picked something." Both look identical on the page: one word. This
lesson adds the missing piece: a confidence score alongside the label,
from the same call.

## Asking for confidence isn't a separate call

The obvious way to add a confidence score would be a second prompt:
classify first, then ask "how sure were you?" as a follow-up. That
doubles the API calls for no real benefit, the model already has an
implicit sense of how sure it is the moment it produces the label, this
lesson just asks it to say that number out loud in the same response,
using the same structured-output approach Lesson 3 used for the label
itself, just with one more field in the schema:

```python
CLASSIFY_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "label": types.Schema(type=types.Type.STRING, enum=LABELS),
        "confidence": types.Schema(type=types.Type.NUMBER),
    },
    required=["label", "confidence"],
)
```

`response_schema` (paired with `response_mime_type="application/json"`)
is Gemini's structured-output contract: the model is constrained to
return JSON matching this shape, `label` one of the three enum values,
`confidence` a number. No parsing a sentence for the word you want, no
regex, the field is just there.

## The code, piece by piece

```python
response = client.models.generate_content(
    model=CHAT_MODEL,
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=CLASSIFY_SCHEMA,
        temperature=0,
    ),
)
result = json.loads(response.text)
return result["label"], float(result["confidence"])
```

Same classify call as Beginner Lesson 3, same `temperature=0` for a
repeatable label, the only change is `response_schema` now describes
two fields instead of one, and the return value is a tuple instead of a
bare string.

## Running it

```bash
uv run python lessons/adaptive_rag/02_intermediate/10_confidence_aware_routing/lesson.py
```

## Expected output

```
Q: What oven setting does the pizza dough recipe use?
  label: simple_factual
  confidence: 1.00

Q: How does wind speed affect things around the house?
  label: ambiguous
  confidence: 0.85
```

The pizza question is a clean, single-document lookup: nothing about
its phrasing points anywhere else, and the model says so with
confidence at or near 1.0. The wind speed question genuinely straddles
two documents, `weather-station.md`'s sensor readings and `garden.md`'s
note about wind drying out the raised beds, with no single-document
phrasing that settles which one the asker meant. Its confidence lands
lower, not because the classifier is broken, but because the question
itself is the kind a classifier should be less sure about.

## Checkpoint

- **confidence score**: a 0 to 1 number returned alongside the label,
  in the same structured-output call, describing how sure the
  classifier is about its own answer.
- A label alone can't tell "clearly this route" apart from "the
  classifier guessed," both render as the same word. Confidence is
  what makes that difference visible.
- Confidence isn't free information from nowhere, it's the model
  reporting on its own uncertainty, which is itself an estimate, not a
  guarantee. Lesson 11 is where this number starts actually changing
  what the router does.

If anything here still feels unclear, ask before moving to Lesson 11.
