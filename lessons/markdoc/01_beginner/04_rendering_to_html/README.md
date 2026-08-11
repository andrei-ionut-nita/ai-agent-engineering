# Lesson 4: Rendering a render tree to HTML

## The problem: a render tree still isn't something a browser can show

Lesson 3's render tree is renderer-agnostic on purpose, it's plain
`Markdoc.Tag` objects and strings, not HTML markup. Something still has
to walk that tree and produce an actual output format. `Markdoc.renderers.html`
is that something, for HTML specifically; Lesson 16 uses
`Markdoc.renderers.react` on the exact same *kind* of tree to produce
React elements instead.

## The code, piece by piece

```javascript
const ast = Markdoc.parse(source);
const renderTree = Markdoc.transform(ast, {});
const html = Markdoc.renderers.html(renderTree);
```

The three-stage pipeline from Lessons 2-3, closed out with the render
step. `Markdoc.renderers.html` returns a plain string, there's no
intermediate DOM or virtual-DOM step, just template-style string
concatenation over the render tree.

```javascript
const handBuiltTree = new Markdoc.Tag("article", {}, [
  new Markdoc.Tag("h1", {}, ["Built without parsing anything"]),
  ...
]);
Markdoc.renderers.html(handBuiltTree);
```

This is the proof that the renderer only cares about the render tree's
shape, not its origin. `new Markdoc.Tag(name, attributes, children)` is
the exact same object type `transform()` produces internally, you rarely
construct one by hand in real usage (custom tag `transform` functions do,
see Lesson 9), but doing it explicitly here makes clear that "render
tree" is just a plain, inspectable JS data structure, not a black box
tied to parsing.

## Running it

```bash
node 01_beginner/04_rendering_to_html/lesson.js
```

## Expected output

```
Final HTML:
<article><h1>Hello, Markdoc</h1><p>This is a short document used across the early lessons in this course.</p><p>It has a <strong>heading</strong>, a paragraph, and a list:</p><ul><li>First item</li><li>Second item</li><li>Third item</li></ul></article>

Rendering a hand-built render tree (no source string involved):
<article><h1>Built without parsing anything</h1><p>This render tree was constructed directly in JavaScript.</p></article>
```

## Checkpoint

- **`Markdoc.renderers.html(renderTree)`**: the final pipeline stage,
  render tree in, HTML string out. It only reads the render tree, never
  the original source or the `Ast`.
- **`new Markdoc.Tag(name, attributes, children)`**: the render tree's
  actual node constructor, a plain, inspectable value you can build by
  hand, which is exactly what a custom tag's `transform` function
  returns (Lesson 9).
- **The pipeline, complete**: parse (Lesson 2) -> transform (Lesson 3) ->
  render (this lesson). Every later lesson in this course builds on top
  of this same three-call shape, mostly by adding things to the config
  object passed to `transform`.

You've finished the core pipeline. Lesson 5 adds one more piece before the
Beginner checkpoint: reading metadata out of a document via frontmatter.
