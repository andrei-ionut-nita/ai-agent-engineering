# Lesson 5 (Beginner checkpoint): convert a whole folder

## No new API, just the loop

This lesson doesn't introduce anything new from MarkItDown's side,
it's the checkpoint: prove Lessons 1-4 add up to something useful by
converting an entire folder of mixed-format files with the same
`.convert(path)` call, one iteration per file, writing real `.md`
files to disk.

This is close to the actual shape of a real ingestion script: point it
at a directory, convert what's there, get Markdown out the other
side, ready to chunk, embed, or feed straight into a prompt.

## Why `office_notice.png` is skipped here

The fixtures folder has six files, this lesson only converts five.
`office_notice.png` is left out on purpose: MarkItDown's image
converter, without an LLM client attached, has nothing to extract from
a photo beyond basic file metadata, there's no OCR or vision model
running by default. Converting it here would just print noise. Lesson
6 revisits this exact file and shows the same conversion with an LLM
client wired in, where the difference becomes the whole point of the
lesson.

## The code, piece by piece

```python
source_files = sorted(
    p for p in FIXTURES_DIR.iterdir() if p.is_file() and p.name not in SKIP
)
```

Lists every file in `fixtures/` except the skipped one, sorted for
deterministic output ordering.

```python
for source_path in source_files:
    result = md.convert(source_path)
    output_path = OUTPUT_DIR / f"{source_path.stem}.md"
    output_path.write_text(result.markdown, encoding="utf-8")
    summary.append((source_path.name, source_path.suffix, len(result.markdown)))
```

Same `.convert()` call from every prior lesson, now in a loop, with
each result written to a same-named `.md` file in a local `converted/`
folder, and a `(name, format, length)` tuple kept for the summary
table.

## Running it

```bash
uv run python lessons/markitdown/01_beginner/05_beginner_checkpoint_project/lesson.py
```

## Expected output

```
Converted 5 files from fixtures/ into /home/nolan/Documents/Projects/ai-agent-engineering/lessons/markitdown/01_beginner/05_beginner_checkpoint_project/converted/

Source file                  Format    Output length (chars)
------------------------------------------------------------
expense_report.xlsx          .xlsx                       435
onboarding_deck.pptx         .pptx                       519
product_spec.pdf             .pdf                        819
release_notes.txt            .txt                        293
remote_work_memo.docx        .docx                      1014
```

(The absolute path in the first line will differ on your machine.) A
`converted/` subfolder now exists alongside this README, with five
`.md` files in it, open one and compare it to its source fixture.

## Checkpoint

- **No new API**: this lesson is Lessons 1-3's `.convert(path)`, in a
  loop, over a real folder.
- **Batch conversion shape**: list files, convert each, write output,
  track a summary, this is the skeleton of a real ingestion script.
- **Images need more**: without an LLM client, image files convert to
  little more than metadata, which is why `office_notice.png` was
  skipped here and saved for Lesson 6.

You've finished the Beginner tier. If anything here still feels
unclear, ask before moving to Lesson 6 and the Intermediate tier.
