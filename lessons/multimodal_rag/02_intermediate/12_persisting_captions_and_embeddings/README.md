# Lesson 12: Persisting Captions and Embeddings

## Where we left off

Every lesson so far re-captions all four images and re-embeds all nine
records on every single run. That was fine for four images; it stops
being fine the moment a corpus has hundreds. Captioning is a vision
call per image (Lesson 4), the most expensive step this course's
pipeline has, more expensive than embedding a text chunk, since it
sends a full image and asks for a paragraph back rather than a short
string and a vector. This lesson applies `naive_rag` Lesson 13's fix
(save to JSON, load instead of rebuild) to that specific cost.

## The code, piece by piece

```python
def save_store(store: list[dict], path: Path) -> None:
    serializable = [
        {**record, "image_path": str(record["image_path"]) if record["image_path"] else None}
        for record in store
    ]
    path.write_text(json.dumps(serializable))
```

One wrinkle `naive_rag` Lesson 13 never had: `image_path` is a `Path`
object, and `json.dumps` doesn't know how to serialize one. Converting
it to a plain string (`None` stays `None`) before saving, and back to a
`Path` after loading, is the entire adaptation needed, everything else
about persistence (a record is JSON-serializable, a vector is just a
list of floats) is identical to the text-only version.

```python
def load_store(path: Path) -> list[dict]:
    records = json.loads(path.read_text())
    for record in records:
        if record["image_path"] is not None:
            record["image_path"] = Path(record["image_path"])
    return records
```

The reverse conversion, run once at load time, restoring `image_path`
to a real `Path` so Lesson 8's generation code (`record["image_path"].read_bytes()`)
keeps working unmodified against a loaded store, exactly as it does
against a freshly built one.

## Running it

```bash
uv run python lessons/multimodal_rag/02_intermediate/12_persisting_captions_and_embeddings/lesson.py
```

Run it twice, delete `store.json` in between to see the difference.

## Expected output

First run (no `store.json` yet):
```
Captioned 4 images and embedded 9 records in 6.1234s, saved to store.json
```

Second run (`store.json` exists):
```
Loaded 9 records from store.json in 0.0012s
(no captioning or embedding calls made, delete store.json to force a rebuild)
```

## Checkpoint

- Captioning is the most expensive step this course's pipeline has,
  one vision call per image; persisting the store avoids re-paying it
  on every run, the same motivation `naive_rag` Lesson 13 had for text
  embeddings, now mattering even more.
- `Path` objects need converting to and from plain strings around a
  JSON round-trip; everything else about the record survives
  unchanged.
- This is still a single flat file, adequate for this course's small
  fixture set; Lesson 20 replaces it with `chromadb`, which persists
  automatically and scales past what a JSON file comfortably handles.

If anything here still feels unclear, ask before moving to Lesson 13.
