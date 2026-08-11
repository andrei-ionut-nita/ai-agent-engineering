# Lesson 3: `Markdoc.transform` and the render tree

## The problem: an `Ast` isn't renderable yet

Lesson 2's `Ast` describes the document's *structure* (this is a heading,
that's a list), but it's a Markdoc-specific shape, not something an HTML
renderer or React can consume directly, and it hasn't resolved anything a
config would supply, no variable values, no custom tags. `transform()` is
the stage that does both: it walks the `Ast` and produces a **render
tree**, a plain, renderer-agnostic tree of `Markdoc.Tag` objects and raw
strings.

## The code, piece by piece

```javascript
const renderTree = Markdoc.transform(ast, {});
```

`transform` takes the `Ast` plus a config object. Passing `{}` here means
no custom tags, variables, or functions are registered, transform still
runs completely, built-in Markdown constructs (headings, paragraphs,
lists, bold text) resolve to their default `Tag` equivalents on their
own, no config entry needed for `heading -> h1` or `list -> ul`, that
mapping is Markdoc's built-in default behavior (the same one Lesson 14
later shows how to override).

```javascript
function describeRenderNode(node, depth = 0) {
  if (typeof node === "string") { ... }
  console.log(`<${node.name}>`, node.attributes);
  for (const child of node.children) { ... }
}
```

Render tree nodes are `Markdoc.Tag` instances with `.name`, `.attributes`,
`.children`, note the field is `.name` here, not `.type` like an `Ast`
node, that's one of several small shape differences between the two
trees. Render tree children can also just be plain strings (raw text),
`Ast` nodes never appear as bare strings the way render tree children do.

## Ast vs. render tree, side by side

| | `Ast` (Lesson 2) | Render tree (this lesson) |
|---|---|---|
| Produced by | `Markdoc.parse(source)` | `Markdoc.transform(ast, config)` |
| Node identity field | `.type` (e.g. `"heading"`) | `.name` (e.g. `"h1"`) |
| Needs a config? | No | Yes (even `{}` counts) |
| Can contain raw strings as children? | No, always nodes | Yes |
| What consumes it | `transform()`, `validate()` | A renderer: `renderers.html`, `renderers.react` |

## Running it

```bash
node 01_beginner/03_transform_and_the_render_tree/lesson.js
```

## Expected output

```
Ast (Lesson 2's shape): root type "document", nodes carry .type + .attributes

Render tree (this lesson's shape): root tag "<article>", nodes carry .name + .attributes + .children

Render tree, walked:
<article>
  <h1>
    "Hello, Markdoc"
  <p>
    "This is a short document used across the early lessons in this course."
  <p>
    "It has a "
    <strong>
      "heading"
    ", a paragraph, and a list:"
  <ul>
    <li>
      "First item"
    <li>
      "Second item"
    <li>
      "Third item"

Ast node types vs render tree tag names for the same content:
  Ast 'heading' (attributes.level=1)  ->  render tree tag 'h1'
  Ast 'paragraph'                     ->  render tree tag 'p'
  Ast 'list' (attributes.ordered=false) -> render tree tag 'ul'
  Ast 'item'                          ->  render tree tag 'li'
```

## Checkpoint

- **`Markdoc.transform(ast, config)`**: the middle pipeline stage,
  `Ast` + config -> render tree. This is where tags, variables, and
  functions actually get resolved (starting Lesson 7).
- **Render tree shape**: `Markdoc.Tag` objects with `.name` /
  `.attributes` / `.children`, plus raw strings as children, distinct
  from the `Ast`'s `.type` / `.attributes` / `.children` shape.
- **Config isn't optional in spirit, even if it's optional in code**: an
  empty `{}` still produces a full render tree, because built-in
  Markdown constructs have default `Tag` mappings baked in.

If anything here still feels unclear, ask before moving to Lesson 4.
