# Lesson 2: The model library, tags, and inspecting a model

## Before this lesson

This lesson assumes you've already run these in a terminal (not
Python), as part of this course's setup:

```bash
ollama pull llama3.2
ollama pull llama3.2:1b
```

`ollama pull` is a CLI command, not a Python function you'd normally
call at runtime: pulling downloads gigabytes of model weights, a
one-time setup step, not something a running program does on every
call. Python code interacts with models that are *already* pulled.

## The model library and tags

Ollama's [model library](https://ollama.com/library) hosts many model
families (Llama, Gemma, Qwen, Mistral, and others), each published
under multiple **tags**: variants of the same family at different
sizes or quantization levels. `llama3.2` with no tag is shorthand for
`llama3.2:latest`; `llama3.2:1b` pins the 1-billion-parameter variant
specifically.

Smaller tags trade answer quality for speed and footprint: `1b` runs
faster and fits in less RAM than the full `3.2` (3B-class) tag, at the
cost of being noticeably less capable. There's no universally "right"
tag, it depends on your hardware and what you're building (Lesson 18
covers this tradeoff in more depth, including quantization itself).

## The code, piece by piece

```python
info = ollama.show(model_name)
```

`ollama.show()` asks the local server for everything it knows about an
already-pulled model: its architecture, parameter count, quantization
level, and the raw prompt template it uses internally. This is the
same information `ollama show llama3.2` prints from the CLI, just
structured as a Python object.

```python
info.details.family
info.details.parameter_size
info.details.quantization_level
```

`.details` bundles the three numbers most people actually care about
day to day: which model family it belongs to, how many parameters it
has, and how aggressively it's been quantized (compressed, at a cost
to precision, covered in Lesson 18).

```python
for model in ollama.list().models:
    ...
    size_gb = model.size / 1_000_000_000
```

`ollama.list()`, from Lesson 1, reports the actual bytes on disk,
which is a different number from parameter count: quantization and
format details mean two models with similar parameter counts can take
up different amounts of space.

## Running it

```bash
uv run python lessons/ollama/01_beginner/02_installing_and_pulling_models/lesson.py
```

## Expected output

```
Comparing two tags of the same model family:

llama3.2:
  family: llama
  parameter size: 3.2B
  quantization: Q4_K_M
llama3.2:1b:
  family: llama
  parameter size: 1.2B
  quantization: Q8_0

Disk footprint of each, from ollama.list():
  llama3.2:1b: 1.32 GB
  llama3.2:latest: 2.02 GB
```

Exact sizes can shift slightly as Ollama updates its published
quantizations, but the shape (four lines of model details, then two
disk sizes) should match. If you see a `ResponseError` instead, the
tag hasn't been pulled yet, rerun the two `ollama pull` commands above.

## Checkpoint

- **Model library**: Ollama's hosted catalog of model families.
- **Tag**: a specific variant of a family (size, quantization), pinned
  after a colon; no tag means `:latest`.
- **`ollama pull`**: a one-time CLI download, not a runtime Python call.
- **`ollama.show()`**: inspect an already-pulled model's architecture,
  parameter count, and quantization from Python.

If anything here still feels unclear, ask before moving to Lesson 3,
where you'll send your first real prompt to a local model.
