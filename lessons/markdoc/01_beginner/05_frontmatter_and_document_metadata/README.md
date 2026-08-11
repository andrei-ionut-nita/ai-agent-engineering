# Lesson 5: Frontmatter and document metadata

## The problem: a document needs to describe itself

A real docs page needs metadata that isn't part of its rendered body: a
title for the page `<title>` tag, an author, a publish date, tags for a
search index. The convention (borrowed from Jekyll, Hugo, and most static
site generators) is a `---`-fenced YAML block at the top of the file.
Markdoc recognizes that block as frontmatter, but it deliberately doesn't
parse the YAML for you.

## The code, piece by piece

```javascript
const rawFrontmatter = ast.attributes.frontmatter;
```

`Markdoc.parse()` captures whatever's between the `---` fences as a
**raw string** on `ast.attributes.frontmatter`. Markdoc stays
frontmatter-format-agnostic on purpose, some tools use YAML, others TOML
or JSON, so it just hands you the raw text and lets you pick a parser.

```javascript
import yaml from "js-yaml";
const frontmatter = yaml.load(rawFrontmatter);
```

This lesson picks `js-yaml`, the most common choice for Markdoc projects
(it's what Markdoc's own documentation examples use). `yaml.load()` turns
the raw string into a plain JS object: `{ title: "Shipping Update", author: "Andrei" }`.

```javascript
const config = {
  variables: { frontmatter, name: "reader", showBanner: true },
};
```

This is the actual wiring: nothing in Markdoc automatically connects
`ast.attributes.frontmatter` to `config.variables.frontmatter`, that
connection is your code, made explicit here. Once it's in
`config.variables`, `{% $frontmatter.title %}` in the document body
resolves it exactly like any other variable, the same mechanism Lesson 7
covers on its own.

## Running it

```bash
node 01_beginner/05_frontmatter_and_document_metadata/lesson.js
```

## Expected output

```
Raw frontmatter string from ast.attributes.frontmatter:
"title: Shipping Update\nauthor: Andrei"

Parsed with js-yaml:
{ title: 'Shipping Update', author: 'Andrei' }

Rendered HTML, frontmatter values now resolved inline:
<article><h1>Shipping Update</h1><p>Written by Andrei.</p><p><strong>Note:</strong> this release is still in beta.</p><p>Hello, reader. Thanks for reading.</p></article>
```

## Checkpoint

- **`ast.attributes.frontmatter`**: the raw, unparsed YAML string between
  a document's `---` fences. Markdoc captures it but never parses it.
- **You choose the parser**: `js-yaml` is the conventional choice; the
  parsed object is plain JS data, nothing Markdoc-specific about it.
- **Wiring it into rendering**: frontmatter only becomes usable inside
  `{% $frontmatter.x %}` once you put it on `config.variables.frontmatter`
  yourself, before calling `Markdoc.transform`.

If anything here still feels unclear, ask before moving to Lesson 6, this
tier's checkpoint project.
