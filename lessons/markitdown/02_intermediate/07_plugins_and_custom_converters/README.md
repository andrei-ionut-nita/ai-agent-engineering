# Lesson 7: plugins and custom converters

## MarkItDown is a registry, not a hardcoded format list

Every converter used in Lessons 1-6, docx, pptx, xlsx, pdf, plain
text, image, is the same kind of object under the hood: a
`DocumentConverter` subclass with two methods, confirmed directly
against `markitdown/_base_converter.py`:

```python
class DocumentConverter:
    def accepts(self, file_stream, stream_info, **kwargs) -> bool:
        """Quick check: should this converter handle this file?"""

    def convert(self, file_stream, stream_info, **kwargs) -> DocumentConverterResult:
        """Do the actual conversion."""
```

`MarkItDown()` builds a list of these, one per built-in format.
`register_converter()` adds your own to that same list. There's no
separate "plugin system" API to learn beyond this, a plugin, in
MarkItDown's own terms, is just a `DocumentConverter` someone else
wrote and packaged.

## Building a converter for a format MarkItDown has never seen

This lesson invents a tiny synthetic format, `.ticket`, a handful of
`key: value` lines meant to look like a support ticket record
(`data/sample_ticket.ticket`). MarkItDown ships no converter for
`.ticket` files.

```python
class TicketConverter(DocumentConverter):
    def accepts(self, file_stream, stream_info, **kwargs):
        return (stream_info.extension or "").lower() == ".ticket"

    def convert(self, file_stream, stream_info, **kwargs):
        raw = file_stream.read().decode("utf-8")
        lines = []
        for line in raw.strip().splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                lines.append(f"- **{key.strip()}**: {value.strip()}")
        return DocumentConverterResult(markdown="\n".join(lines), title="Support Ticket")
```

`accepts()` should be cheap, it's called on every registered converter
to find a match, here it's a plain extension check. `convert()` only
runs once `accepts()` said yes, and turns the raw text into a bulleted
Markdown list with a title.

## What happens before you register it: not a hard failure

You might expect an unregistered format to raise an exception. It
doesn't, not for a text-ish file like this one. MarkItDown's built-in
`PlainTextConverter` is registered as a low-priority fallback that
accepts a broad range of text content, so a `.ticket` file, being
valid UTF-8, still "converts", the raw `key: value` lines pass through
completely unstructured, with none of the bullet-list formatting a
purpose-built converter would add. That gap, working but not
*good*, is exactly what a custom converter fixes.

## The code, piece by piece

```python
md.register_converter(TicketConverter())
```

Adds the converter to MarkItDown's registry. Per the docstring in
`markitdown/_markitdown.py`, custom converters are inserted ahead of
previously registered ones by default, so a custom converter can even
override a built-in one for a format MarkItDown already knows, not
just add support for a new one.

```python
result = md.convert_stream(io.BytesIO(sample_bytes), file_extension=".ticket")
```

Same conversion call as always, `.convert_stream()` from Lesson 4,
MarkItDown now finds `TicketConverter.accepts()` returns `True` for
`.ticket` and routes the file to it instead of the plain-text fallback.

## Running it

```bash
uv run python lessons/markitdown/02_intermediate/07_plugins_and_custom_converters/lesson.py
```

## Expected output

```
=== Before registering TicketConverter (falls back to plain text) ===

Title: None
Markdown:
id: 4821
priority: high
subject: VPN drops every 10 minutes
requester: dana.ortiz@northwindgadgets.example


=== After registering TicketConverter ===

Title: Support Ticket
Markdown:
- **id**: 4821
- **priority**: high
- **subject**: VPN drops every 10 minutes
- **requester**: dana.ortiz@northwindgadgets.example
```

## Checkpoint

- **`DocumentConverter`**: the base class every converter, built-in or
  custom, implements: `accepts()` (should I handle this?) and
  `convert()` (do it).
- **`register_converter()`**: adds a converter to MarkItDown's
  registry, inserted ahead of existing ones by default, can even
  override a built-in converter.
- **Unregistered text-ish formats don't hard-fail**: `PlainTextConverter`
  is a low-priority fallback for text content, so an unrecognized
  format often still "converts", just without any real structure.

If anything here still feels unclear, ask before moving to Lesson 8.
