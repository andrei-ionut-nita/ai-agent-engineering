# Lesson 7: Managing models from Python

## Four operations, one theme: models are files on your disk

Every model you pull takes up real, permanent disk space until you
remove it, unlike a cloud API, where "using a model" never costs you
storage. This lesson covers the four operations that keep that under
control, all available from Python even though you'd typically reach
for the `ollama` CLI directly for most of them day to day.

## `ollama.pull()`: rarely called at runtime

```python
ollama.pull(THROWAWAY_MODEL)
```

The Python equivalent of `ollama pull` on the CLI. This lesson calls
it directly so there's a disposable model to safely delete later, but
in a real program you'd almost never pull a model at runtime: it's a
multi-hundred-megabyte-to-multi-gigabyte download, not something you
want happening the first time a user makes a request.

## `ollama.list()` vs `ollama.ps()`: on disk vs in memory

```python
on_disk = [model.model for model in ollama.list().models]
```

`ollama.list()`, from Lessons 1 and 2, reports everything ever pulled,
sitting on disk, whether or not it's currently in use. That's the
"installed" list.

```python
loaded = ollama.ps().models
```

`ollama.ps()` (mirroring the Unix `ps` command for running processes)
reports only what's currently loaded into memory or GPU VRAM right
now, ready to answer instantly. Ollama automatically unloads a model
after a few minutes of inactivity to free that memory back up, which
is why `expires_at` shows up on each entry: it's when Ollama plans to
unload it if nothing else asks for it first.

## `ollama.delete()`: freeing disk space

```python
ollama.delete(THROWAWAY_MODEL)
```

The Python equivalent of `ollama rm`. Removes the model's weights from
disk permanently, gone until you `pull` it again. This is the one
operation genuinely worth knowing from Python: a long-running
application that manages its own local models (Lesson 22 builds one
that runs as a background service) may need to clean up old or unused
models on its own, without a human running CLI commands.

## Running it

```bash
uv run python lessons/ollama/01_beginner/07_listing_and_managing_models/lesson.py
```

This pulls `qwen2.5:0.5b` (under 500 MB) and deletes it again by the
end, so it doesn't take up permanent space on your machine.

## Expected output

The exact list order, VRAM size, and `expires_at` timestamp depend on
your machine and what else you've run recently, but the shape matches:

```
Pulling qwen2.5:0.5b ...

On disk now: ['qwen2.5:0.5b', 'llama3.2:1b', 'llama3.2:latest', 'llama3:latest']

Currently loaded in memory:
  llama3.2:latest (2.75 GB in memory, expires 2026-08-07 10:44:56.247184+01:00)

Deleting qwen2.5:0.5b ...
On disk after delete: ['llama3.2:1b', 'llama3.2:latest', 'llama3:latest']
```

If "Currently loaded in memory" prints nothing, that's fine too, it
just means no model happened to be loaded from a previous lesson's run
at the moment you ran this one.

## Checkpoint

- **`ollama.pull()`**: downloads a model's weights to disk, rarely
  called at runtime in a real program.
- **`ollama.list()`**: everything on disk, "installed."
- **`ollama.ps()`**: what's currently loaded in memory, "running,"
  auto-unloaded after a few idle minutes.
- **`ollama.delete()`**: permanently frees disk space, the one
  operation worth calling from a real long-running program.

If anything here still feels unclear, ask before moving to Lesson 8.
