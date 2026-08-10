# Lesson 4: converting from streams and URLs

## Three entry points, one underlying job

MarkItDown has more than one method for getting bytes in, they all
end up doing the same conversion work, they just differ in where the
bytes come from:

| Method | Input | Typical use |
|---|---|---|
| `.convert(path)` | A file path on disk | Files you already have locally (Lessons 1-3) |
| `.convert_stream(file_obj, ...)` | An open, readable binary stream | Uploaded files that never touch disk, in-memory bytes |
| `.convert_url(url)` | A URL string | Web pages, remote documents fetched over HTTP |

This isn't the full list, `convert_uri()` handles `data:` and `file:`
URIs, `convert_response()` wraps an already-fetched `requests.Response`
directly, but stream and URL are the two you'll reach for most, and
the pattern generalizes to the rest.

## Why streams need a hint that paths don't

`.convert(path)` can look at the file's extension (`.docx`, `.pdf`,
...) to help decide which converter to use. An open binary stream,
`open(path, "rb")`, has no filename attached to it once it's just
bytes, so MarkItDown has nothing to go on unless you tell it. That's
why `convert_stream()` in this lesson passes `file_extension=".docx"`
explicitly: without it, auto-detection would have to guess purely from
content, which works for some formats and not others. Lesson 8 covers
the fuller `StreamInfo` object, which lets you specify extension,
mimetype, and charset together for trickier cases.

## `convert_url()` makes a real network call

Unlike every other lesson so far, this one talks to the internet.
`https://books.toscrape.com/` is a public site built specifically for
scraping practice (the same reason
`lessons/playwright/01_beginner/04_navigating_to_a_page/` uses it), so
it's about as stable a target as a live URL gets, but it's still live:
if the site is down or unreachable, this call raises an exception with
nothing to do with MarkItDown's own logic.

## The code, piece by piece

```python
with open(docx_path, "rb") as f:
    stream_result = md.convert_stream(f, file_extension=".docx")
```

The file is opened in binary mode (`"rb"`), MarkItDown needs raw
bytes, and the extension hint is passed as a keyword argument.

```python
url_result = md.convert_url("https://books.toscrape.com/")
```

One call fetches the page and converts its HTML to Markdown. The
result is the same `DocumentConverterResult` shape as every other
conversion in this course, `.markdown`, `.title`, etc.

## Running it

```bash
uv run python lessons/markitdown/01_beginner/04_converting_from_streams_and_urls/lesson.py
```

## Expected output

The docx portion is deterministic. The URL portion depends on the live
site's current HTML, the character count and exact content could shift
slightly if the site changes, but the general shape (a nav menu,
category links, "Books to Scrape") should hold:

```
=== convert_stream() on remote_work_memo.docx ===

Internal Memo: Remote Work Equipment Policy

To: All Northwind Gadgets Staff

From: Facilities and IT Department

Date: June 2026

Summary

Starting this quarter, every employee working remotely more 
...

=== convert_url() on https://books.toscrape.com/ ===

Converted length: 10478 characters
First 400 characters:

[Books to Scrape](index.html) We love being scraped!

* [Home](index.html)
* All products

* [Books](catalogue/category/books_1/index.html)
  + [Travel](catalogue/category/books/travel_2/index.html)
  + [Mystery](catalogue/category/books/mystery_3/index.html)
  + [Historical Fiction](catalogue/category/books/historical-fiction_4/index.html)
  + [Sequential Art](catalogue/category/books/sequential-
```

## Checkpoint

- **Three entry points**: `.convert(path)`, `.convert_stream(file_obj)`,
  `.convert_url(url)`, same underlying conversion, different byte
  sources.
- **Streams need a hint**: an open stream has no filename, pass
  `file_extension` (or fuller `StreamInfo`, Lesson 8) so auto-detection
  has something to work with.
- **`convert_url()` is a live network call**: non-deterministic content,
  can fail for reasons that have nothing to do with MarkItDown.

If anything here still feels unclear, ask before moving to Lesson 5.
