# Lesson 11: Partials

## The problem: repeated content shouldn't live in every file that needs it

A shared disclaimer, a common install-step callout, a footer, these
show up on many pages of a docs site. Copy-pasting them into every source
file means every edit has to happen N times. Markdoc's `{% partial %}`
tag lets one document include another, but with a twist: **Markdoc
itself never touches the filesystem**. Resolving `file="..."` to actual
content is entirely your code's responsibility.

## The code, piece by piece

```javascript
const partialSource = fs.readFileSync(path.join(FIXTURES_DIR, partialPath), "utf8");
const partialAst = Markdoc.parse(partialSource);
```

Reading the partial's file and parsing it happens exactly the same way
as any other document, `Markdoc.parse` doesn't have a special "this is a
partial" mode.

```javascript
const config = {
  tags: { callout },
  partials: { [partialPath]: partialAst },
};
```

`config.partials` is a plain map: the **exact string** used in the
source's `file="..."` attribute, mapped to that file's already-parsed
`Ast`. When `transform` encounters `{% partial file="partials/callout.md" /%}`,
it looks up `config.partials["partials/callout.md"]`, if that key isn't
there, the partial silently resolves to nothing during a render, but
`Markdoc.validate` (below) reports it as a real error.

```
{% partial file="partials/callout.md" /%}
```

Note the trailing `/%}`, `partial` is a self-closing tag (it has no
children of its own, it's replaced entirely by whatever the referenced
file contains), Markdoc's own built-in tag schema for `partial` marks it
`selfClosing: true`.

```javascript
const errors = Markdoc.validate(ast, { tags: { callout } });
```

Validating the same document *without* `config.partials` set reproduces
exactly the "Partial not found" error a CI check would catch, this is
what makes a missing or renamed partial a build-time failure instead of a
silently broken page.

## Running it

```bash
node 02_intermediate/11_partials/lesson.js
```

## Expected output

```
Partial file resolved manually and added to config.partials:
  "partials/callout.md" -> parsed Ast (1 top-level node(s))

Rendered HTML, partial content now inlined:
<article><h1>Getting started</h1><p>Follow these steps to get set up.</p><Callout type="info"><p>This content is shared across every page that includes this partial.</p></Callout><p>Then run the CLI.</p></article>

Validating the same document with an EMPTY config.partials:
  attribute-value-invalid: Partial `partials/callout.md` not found. The 'file' attribute must be set in `config.partials`
```

## Checkpoint

- **`{% partial file="..." /%}`**: a self-closing built-in tag that
  includes another document's content inline.
- **Markdoc does zero filesystem I/O**: `config.partials` must already
  contain every referenced file's parsed `Ast`, resolving paths and
  reading files is entirely host code, exactly like the frontmatter
  parsing in Lesson 5.
- **A missing partial is a validation error, not a silent gap**:
  `Markdoc.validate` reports `attribute-value-invalid` with a clear
  message when a `file` isn't in `config.partials`, catchable in CI
  before a broken page ships.

If anything here still feels unclear, ask before moving to Lesson 12.
