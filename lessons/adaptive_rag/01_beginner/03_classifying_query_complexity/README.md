# Lesson 3: Classifying Query Complexity by Hand

## Where we left off

Lesson 2 named what each strategy is good at, in terms of the kind of
question it handles well: naive retrieval for single-fact lookups,
graph-style traversal for questions whose answer spans documents,
correction for questions that came back wrong the first time. Before any
of that routing can happen, something has to look at the raw question
and decide which of those categories it falls into. That's this lesson:
a classifier, nothing more, no routing or retrieval yet.

## Three labels, one structured call

This course uses three labels for the rest of the Beginner tier:

- `simple_factual`: one document has the whole answer.
- `multi_hop`: the answer needs two or more documents combined.
- `ambiguous`: underspecified, or the answer draws on multiple documents
  from different angles with no clearly-right document to check first.

Asking Gemini to just "say the label" in plain text works most of the
time, but plain text is fragile to parse: the model might wrap the
label in a sentence, use different capitalization, or add punctuation.
`response_mime_type="application/json"` plus `response_schema` fixes
that at the API level, Gemini is constrained to return JSON matching the
schema, not merely asked nicely to.

## The code, piece by piece

```python
class Classification(BaseModel):
    label: str  # one of: simple_factual, multi_hop, ambiguous
    reason: str
```

A small Pydantic model describing exactly the shape of the response
this lesson wants back: a label, and a one-sentence reason. Passing this
class as `response_schema` (rather than hand-writing a JSON schema dict)
lets Gemini's SDK derive the schema automatically from the model's
fields and types.

```python
response = client.models.generate_content(
    model=CHAT_MODEL,
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=Classification,
        temperature=0,
    ),
)
return Classification.model_validate_json(response.text)
```

`response_mime_type="application/json"` tells Gemini the reply must be
JSON. `response_schema=Classification` tells it exactly which JSON
shape. `temperature=0` isn't strictly required for the schema to be
honored, but a classification task benefits from the model's least
random setting, the label shouldn't wobble between runs on the same
question. `Classification.model_validate_json(...)` parses the raw JSON
string straight back into a typed Python object, no manual `json.loads`
plus dict-key access needed.

## Three example questions, one per label

This lesson deliberately tests one question per label, chosen from this
course's fixtures:

- *"What oven setting does the pizza dough recipe use?"* -
  `pizza-dough.md` alone answers this, `simple_factual`.
- *"What two hobbies happen in the same room as the weather station?"* -
  `bookshelf.md` and `cello-practice.md` each name one hobby and confirm
  the room independently, `multi_hop`.
- *"How does wind speed affect things around the house?"* - wind speed
  appears in `weather-station.md` (sensor readings drifting) and
  `garden.md` (drying out the raised beds), two different angles with no
  single obviously-right document, `ambiguous`.

## Running it

```bash
uv run python lessons/adaptive_rag/01_beginner/03_classifying_query_complexity/lesson.py
```

## Expected output

```
Q: What oven setting does the pizza dough recipe use?
  label:  simple_factual
  reason: <a sentence explaining why one document suffices>

Q: What two hobbies happen in the same room as the weather station?
  label:  multi_hop
  reason: <a sentence explaining why two documents are needed>

Q: How does wind speed affect things around the house?
  label:  ambiguous
  reason: <a sentence explaining why this spans documents without a clear single source>
```

The exact reason text varies each run, but with `temperature=0` the
three labels themselves should come back consistently as
`simple_factual`, `multi_hop`, and `ambiguous`, in that order.

## Checkpoint

- **structured output**: `response_mime_type="application/json"` plus
  `response_schema` constrains Gemini's reply to a specific, reliably
  parseable shape, instead of hoping a plain-text instruction gets
  followed exactly.
- A Pydantic `BaseModel` passed as `response_schema` is enough, the SDK
  derives the JSON schema from it automatically.
- Three labels, `simple_factual`, `multi_hop`, `ambiguous`, are this
  course's whole routing vocabulary for the Beginner tier.

If anything here still feels unclear, ask before moving to Lesson 4.
