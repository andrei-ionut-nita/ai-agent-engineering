# Lesson 5 (Checkpoint): Batch-parsing a folder of PDFs

## Putting the beginner tier together

Four lessons in, you have everything a real first pipeline step needs:
build one parser (Lesson 3's `ocr_enabled=False` for known native-text
documents), run `.parse()` over every file in a folder (Lesson 2), and
read back `.text` and `.num_pages` for each (Lessons 2 and 4). This
checkpoint does exactly that over the entire `sample_data/` folder and
writes one `.txt` file per PDF, the shape of the very first stage in
almost any document-processing pipeline: PDFs in, plain text out,
everything downstream (chunking, embedding, search) reads text files or
strings, not PDFs.

## The code, piece by piece

```python
pdf_paths = sorted(SAMPLE_DATA_DIR.glob("*.pdf"))
```

Globs only the top-level `.pdf` files in `sample_data/`, which leaves
out the `_src/` subfolder (the plain-text/PNG sources those PDFs were
originally built from, not something to parse).

```python
parser = liteparse.LiteParse(ocr_enabled=False, quiet=True)
```

One parser, reused across every file in the loop, `ocr_enabled=False`
since these are all documents you already know the nature of.

```python
for pdf_path in pdf_paths:
    result = parser.parse(pdf_path)
    txt_path = output_dir / f"{pdf_path.stem}.txt"
    txt_path.write_text(result.text, encoding="utf-8")
```

The core loop: parse, then write `.text` straight to a `.txt` file with
the same base name. Output goes to a temp directory (`tempfile.mkdtemp`)
so running this lesson repeatedly never leaves generated files lying
around in the repo, in a real pipeline you'd point `output_dir` at
wherever your next stage reads from.

## Why `scanned_notice.pdf` comes back empty

This batch deliberately includes `scanned_notice.pdf`, a genuinely
scanned page with no extractable text layer at all (it was built by
rendering a PNG image into a PDF, there's no text object in it for
LiteParse to find). With `ocr_enabled=False`, LiteParse never attempts
to recover text from the rendered page image, so its `.txt` output is
empty. This isn't a bug in this lesson, it's the realistic shape of a
mixed batch: some PDFs need OCR and some don't, and Lesson 8 covers how
to tell the difference and turn OCR on for the ones that need it.

## Running it

```bash
uv run python lessons/liteparse/01_beginner/05_beginner_checkpoint_project/lesson.py
```

## Expected output

```
Writing .txt output to: /tmp/liteparse_lesson05_jgpe3srh

file                      pages    chars  txt_output
----------------------------------------------------------------------
employee_handbook.pdf         1     1070  employee_handbook.txt
intake_form.pdf               1      158  intake_form.txt
product_spec.pdf              1      677  product_spec.txt
scanned_notice.pdf            1        0  scanned_notice.txt
vendor_memo.pdf               1      242  vendor_memo.txt
----------------------------------------------------------------------
5 file(s) parsed, 2147 total characters written

Note: scanned_notice.pdf shows 0 characters here, it's a genuinely scanned page with no text layer, and ocr_enabled=False means LiteParse never tries to recover its text via OCR. Lesson 8 covers exactly this contrast.
```

The temp directory path will differ on your machine each run.

## Checkpoint

- A batch parse is just the same `.parse()` call in a loop, over one
  reused, pre-configured `LiteParse()` instance.
- `.text` written straight to a file is the whole first stage of most
  document pipelines.
- A mixed batch of native-text and scanned PDFs will not parse
  uniformly well with OCR off, and knowing which files came back
  (near-)empty is itself useful pipeline information.

This closes out the beginner tier. If anything from Lessons 1-5 still
feels unclear, ask before moving to Lesson 6 and the intermediate tier.
