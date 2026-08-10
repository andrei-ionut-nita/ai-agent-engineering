# Lesson 10: Structure tree and accessibility

## Tagged PDF: a hidden second document

A plain PDF is really just drawing instructions: "put this glyph at
this x/y." Nothing in that inherently says "this line is a heading" or
"these three lines are one paragraph," a human reader infers that from
layout. A **tagged PDF** carries an explicit logical structure tree
alongside the drawing instructions: a real tree of elements (`Document`,
`H1`, `P`, `Table`, `Figure`, ...) that says what each piece of content
*is*, independent of how it's positioned on the page.

This is the same mechanism `<h1>`, `<p>`, and `<table>` provide in
HTML, added to PDF specifically so screen readers can read a document
aloud in a sensible logical order (title, then body paragraphs, not
whatever order the PDF happens to draw glyphs in) instead of guessing.
It's opt-in at authoring time; the PDFs in this course have it because
LibreOffice adds structure tags automatically when exporting from a
text document.

## `extract_structure_tree` and `StructureTreeElement`

```python
parser = liteparse.LiteParse(extract_structure_tree=True, ...)
tree = result.pages[0].structure_tree
```

`page.structure_tree` is a `StructureTree` with a `roots` list (usually
one root per page, a `Document` element here). Each `StructureTreeElement`
has:

- `type`: the tag, e.g. `"Document"`, `"P"`, `"H1"`, `"Table"`.
- `children`: nested elements, forming a real tree.
- `actual_text` / `alt_text`: accessibility overrides, present when the
  author supplied one (a screen-reader-only description of an image,
  for example). `None` when absent, as on this course's plain-text
  fixtures.
- `marked_content_ids`: links this structural element back to the
  actual content stream, the mechanism a renderer uses to connect "this
  is a paragraph" to the specific glyphs that make it up.

On `employee_handbook.pdf`, the tree is a single `Document` root with
20 `P` (paragraph) children, one per paragraph LibreOffice recognized
when exporting the handbook's sections.

## Why this matters beyond screen readers

The same tree that lets assistive technology read a document in order
is useful ground truth for a parsing pipeline: instead of inferring
"this looks like a heading because the font is bigger," a tagged PDF
tells you directly. Not every PDF is tagged (many PDFs, especially
older or programmatically generated ones, have no structure tree at
all, in which case `tree.roots` comes back empty), so treat it as a
bonus signal when present, not something to depend on universally.

## Running it

```bash
uv run python lessons/liteparse/02_intermediate/10_structure_tree_and_accessibility/lesson.py
```

## Expected output

```
lessons/liteparse/sample_data/employee_handbook.pdf structure tree: 1 root element(s)

<Document>
  <P>
  <P>
  <P>
  <P>
  <P>
  <P>
  <P>
  <P>
  <P>
  <P>
  <P>
  <P>
  <P>
  <P>
  <P>
  <P>
  <P>
  <P>
  <P>
  <P>

20 tagged <P> (paragraph) element(s) found under the root
```

## Checkpoint

- A tagged PDF carries a logical structure tree alongside its visual
  layout, `extract_structure_tree=True` exposes it via
  `page.structure_tree`.
- `StructureTreeElement.type` is the tag (`Document`, `P`, `H1`,
  `Table`, ...); `children` form a real tree matching document logic,
  not page position.
- Tagging is opt-in and not universal, an untagged PDF returns an empty
  `roots` list, this is a bonus signal, not a guarantee.

This closes out the core intermediate features. Lesson 11 combines
several of them into one checkpoint project. If anything here still
feels unclear, ask before moving on.
