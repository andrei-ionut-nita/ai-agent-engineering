# Lesson 9 (Intermediate checkpoint): a "drop folder" converter

## Combining what the last three lessons built

This checkpoint doesn't introduce new MarkItDown API. It combines:

- **Lesson 5's loop**: convert every file in a folder, write `.md`
  output, track a summary.
- **Lesson 7's custom converter**: `register_converter()`, so the
  synthetic `.ticket` format is understood before the loop even runs.
- **Lesson 8's lesson about failure modes**: format detection isn't
  infallible, and this time the failure is a real one worth handling,
  not a silently-wrong hint but a file nothing can convert at all.

The result is close to a real "drop folder" ingestion job: a
service that watches a directory, converts whatever lands in it, and
has to keep running even when something in that directory isn't a
format it understands.

## The one new thing: handling `UnsupportedFormatException`

Lesson 5's `fixtures/` folder never triggered a real failure, every
file in it was something MarkItDown could convert. This lesson's
`data/` folder has three files: two `.ticket` files (handled by
`TicketConverter`, registered up front) and one `firmware_blob.bin`, a
stand-in for "someone dropped a file into this folder that doesn't
correspond to any known format", raw binary bytes with no structure a
text-oriented converter could make sense of.

```python
try:
    result = md.convert(source_path)
except UnsupportedFormatException:
    results.append((source_path.name, "SKIPPED (unsupported format)", 0))
    continue
```

`UnsupportedFormatException` (from `markitdown._exceptions`) is what
`.convert()` raises when no registered converter, built-in or custom,
claims a file. Catching it and moving on is what turns this from a
script that dies on the first weird file into one that processes an
entire real-world folder, warts and all.

## The code, piece by piece

```python
md.register_converter(TicketConverter())
```

Same registration from Lesson 7, done once before the loop starts, so
every `.ticket` file the loop encounters is already handled by the
time `.convert()` is called on it.

```python
for source_path in source_files:
    try:
        result = md.convert(source_path)
    except UnsupportedFormatException:
        results.append((source_path.name, "SKIPPED (unsupported format)", 0))
        continue
    ...
```

The loop body is Lesson 5's, with one branch added: a file that fails
conversion gets logged as skipped instead of crashing the run.

## Running it

```bash
uv run python lessons/markitdown/02_intermediate/09_intermediate_checkpoint_project/lesson.py
```

## Expected output

```
Processed 3 files from data/

File                     Status                        Output length
--------------------------------------------------------------------
firmware_blob.bin        SKIPPED (unsupported format)              -
printer_ticket.ticket    converted                               154
vpn_ticket.ticket        converted                               130
```

A `converted/` subfolder now has two `.md` files in it, one per
`.ticket` source, `firmware_blob.bin` produced no output file, exactly
as the summary reports.

## Checkpoint

- **This lesson is a combination, not new API**: Lesson 5's loop +
  Lesson 7's `register_converter()` + real error handling.
- **`UnsupportedFormatException`**: raised when no converter, built-in
  or custom, accepts a file. Catch it in a batch job so one bad file
  doesn't stop the whole run.
- **The drop-folder pattern**: register custom converters up front,
  loop over the directory, catch per-file failures, keep a summary,
  this is close to the real shape of an ingestion service.

You've finished the Intermediate tier. If anything here still feels
unclear, ask before moving to Lesson 10 and the Advanced tier.
