# Lesson 19: exporting and versioning flows

## Where we left off

`flow.json` has been sitting in git alongside every lesson's
`lesson.py` since Lesson 2, `git add`-able, `git diff`-able, technically
a real file like any other. This lesson is about the "technically,"
what a plain text diff of `flow.json` actually tells a reviewer (not
much), and the two `lfx` commands worth running on one before it's
committed.

## Why flow.json doesn't code-review like Python

Open any `flow.json` in this course and diff it against a version with
one field changed, the diff is enormous: every node carries its
absolute canvas position, every field its full schema definition
restated, a one-line change in intent (a different system prompt) can
touch hundreds of lines of JSON. A reviewer reading that diff can't
easily tell "what changed" from "what didn't," the way they could with
a one-line Python diff. `flow.json` is worth versioning (it's the
actual, reproducible artifact, better than nothing), it's just not a
substitute for the review quality plain code gets, that gap is a real
part of the prototype-to-production trade-off this course keeps coming
back to.

## Do this yourself

```bash
uv run lfx validate lessons/langflow/01_beginner/02_first_flow/flow.json
```

Run this yourself. Every `flow.json` shipped by this course so far
fails it, missing a top-level `id` field, because `graph.dump()`
(what every earlier lesson used to produce its `flow.json`) doesn't set
one, only the server does, when you save or upload a flow through it.
This isn't a bug in those lessons, `run_flow_from_json` and the REST
API's upload endpoint both work fine without it, `lfx validate` is
simply a stricter check than either of those requires.

## The code, piece by piece

```python
run_lfx("validate", str(SOURCE_FLOW))
```

`lfx validate` checks a flow's structural shape, the kind of thing
worth running in CI on every `flow.json` a pull request touches, before
anyone even opens it.

```python
flow_data["id"] = str(uuid.uuid4())
```

The actual fix: a real flow gets its `id` from the server the moment
it's saved or uploaded there, this lesson generates one directly to
show `validate` passing once it's present.

```python
run_lfx("upgrade", str(FLOW_PATH))
```

A different check: whether each component in the flow still matches
what your *installed* Langflow version expects. Run this after
upgrading the `langflow`/`lfx` package itself, a component marked
`BLOCKED` here is worth investigating before you trust that flow still
behaves the way it did on the older version.

## Running it

```bash
uv run python lessons/langflow/03_advanced/19_exporting_and_versioning_flows/lesson.py
```

No running Langflow server is required for this one.

## Expected output

Exact for the pass/fail lines, the `upgrade` line's exact wording may
shift with the installed Langflow version:

```
validate, as shipped (no top-level id):
✗ .../02_first_flow/flow.json
  [L1 ERROR] Missing required top-level field: 'id'

validate, with an id added:
✓ .../19_exporting_and_versioning_flows/flow.json

upgrade check:
[OK] Chat Input (ChatInput) - id: ChatInput-iRCW7
  [OK] Chat Output (ChatOutput) - id: ChatOutput-qrfhV
  [BLOCKED] Google Generative AI (GoogleGenerativeAIModel) - id: GoogleGenerativeAIComponent-a2YHI
```

## Checkpoint

- **`flow.json`'s diff problem**: a real, versionable artifact, but a
  large, mostly-noise diff compared to an equivalent code change, a
  genuine cost of the visual-builder trade-off.
- **`lfx validate`**: a structural check, worth running in CI, catches
  things like a missing `id` before they surface as a confusing runtime
  error somewhere else.
- **`lfx upgrade`**: a compatibility check against your installed
  Langflow version, worth running after upgrading the package.

If anything here still feels unclear, ask before moving to Lesson 20.
