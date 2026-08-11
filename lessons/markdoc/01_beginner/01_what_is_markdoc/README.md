# Lesson 1: What is Markdoc?

## The problem: Markdown alone can't be validated or templated

Plain Markdown is great for prose, but the moment you want anything more
structured, a warning callout, a tabbed code sample, a value that changes
per environment, you're stuck either writing raw HTML inside your `.md`
files or reaching for a full templating language. Neither is great: raw
HTML isn't checkable (a typo in a `<div>` just silently breaks), and a
general templating language (Handlebars, Jinja) doesn't know anything
about Markdown's own structure.

**Markdoc** is Stripe's open-source answer: a Markdown-based syntax that
adds tags (`{% callout %}`), variables (`{% $name %}`), and functions
(`{% uppercase($title) %}`) on top of standard Markdown, plus a schema you
can use to validate that a document's tags are used correctly before you
ever render it. It's the format Stripe's own public docs are written in.

## Three stages, not one

Most Markdown libraries (`marked`, `remark`, `markdown-it`) do one thing:
source string in, HTML string out, in a single call you don't get to
inspect or redirect. Markdoc instead splits that into three distinct
stages, each with its own function:

| Stage | Function | Input | Output |
|---|---|---|---|
| Parse | `Markdoc.parse(source)` | a source string | an `Ast` node tree |
| Transform | `Markdoc.transform(ast, config)` | an `Ast` + a config (tags, variables, functions) | a render tree (plain `Tag` objects) |
| Render | `Markdoc.renderers.html(renderTree)` | a render tree | a final HTML string |

Splitting it this way is what makes the rest of Markdoc possible: you can
inspect or validate the `Ast` before deciding whether to transform it at
all (Lesson 10), and you can feed the *same* render tree into a different
renderer, HTML today, React in Lesson 16, without re-parsing or
re-transforming anything.

## The code, piece by piece

```javascript
const ast = Markdoc.parse(source);
```

Parsing never looks at a config. It just turns a Markdoc source string
into an `Ast`, Markdoc's word for the parsed node tree, `ast.type` is
always `"document"` at the root.

```javascript
const renderTree = Markdoc.transform(ast);
```

Transform is where tags, variables, and functions actually get resolved.
With no config passed (as here), transform still runs, it just has no
custom tags/variables to resolve, so plain Markdown constructs (headings,
paragraphs, bold text) become the render tree's `Tag` objects on their
own. Every Markdoc document's render tree is wrapped in a top-level
`article` tag.

```javascript
const html = Markdoc.renderers.html(renderTree);
```

The HTML renderer walks the render tree and produces a plain string.
`Markdoc.renderers.react` (Lesson 16) walks the exact same kind of tree
and produces React elements instead, the render tree itself doesn't know
or care which renderer will eventually consume it.

## Running it

```bash
node 01_beginner/01_what_is_markdoc/lesson.js
```

## Expected output

```
Plain Markdown, one step:
  A typical Markdown library (marked, remark, etc.) does one thing: source string in, HTML string out, in a single step you don't control.

Markdoc, three steps:
  Markdoc splits that single step into three: parse (source -> Ast), transform (Ast + config -> render tree), render (render tree -> HTML, React, or anything else you write a renderer for).

source:      "Hello, **Markdoc**.\n"
ast.type:    document
renderTree:  article tag, 1 child(ren)
html:        <article><p>Hello, <strong>Markdoc</strong>.</p></article>

The whole pipeline in one line:
  Markdoc.renderers.html(Markdoc.transform(Markdoc.parse(source)))
```

## Checkpoint

- **Markdoc**: Stripe's open-source Markdown-based authoring format,
  built to add tags, variables, functions, and schema validation on top
  of standard Markdown.
- **Three stages, not one**: `parse` (string -> `Ast`), `transform`
  (`Ast` + config -> render tree), `render` (render tree -> final
  output). Each stage is a separate function call you control.
- **Why split it up**: it lets you validate a document before rendering
  it (Lesson 10), and target multiple output formats (HTML, React) from
  the same render tree without re-parsing.
- **The `article` wrapper**: every document's render tree is wrapped in a
  top-level `article` tag by default, visible in this lesson's output.

If anything here still feels unclear, ask before moving to Lesson 2.
