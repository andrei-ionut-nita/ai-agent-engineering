# Lesson 6: Beginner checkpoint project

## The problem: prove the pipeline works on more than one hand-picked file

Lessons 1-5 each ran the pipeline on one fixture at a time, chosen for
you. This checkpoint has no new Markdoc API, it's a small script that
puts the pieces together on a whole folder: every top-level `.md` file in
`fixtures/`, converted to HTML, written to disk.

## The code, piece by piece

```javascript
const mdFiles = fs
  .readdirSync(FIXTURES_DIR, { withFileTypes: true })
  .filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
  .map((entry) => entry.name)
  .sort();
```

Only top-level `.md` files, not `fixtures/partials/`. Partial files
(Lesson 11) aren't meant to be converted standalone, they're meant to be
included inside other documents via `config.partials`.

```javascript
function convertFile(filename) {
  const ast = Markdoc.parse(source);
  const frontmatter = ast.attributes.frontmatter ? yaml.load(...) : {};
  const config = { variables: { frontmatter, name: "reader", showBanner: true } };
  const renderTree = Markdoc.transform(ast, config);
  const html = Markdoc.renderers.html(renderTree);
  return { nodeCount: countNodes(ast), html };
}
```

The exact Lesson 1-5 pipeline, applied per file: `hello.md` has no
frontmatter (`ast.attributes.frontmatter` is `undefined`, so `frontmatter`
falls back to `{}`), `article.md` does, and its `{% $frontmatter.title %}`
references resolve the same way Lesson 5 demonstrated.

```javascript
function countNodes(node) {
  return 1 + node.children.reduce((sum, child) => sum + countNodes(child), 0);
}
```

A plain recursive count over the `Ast` (not the render tree), used only
for this lesson's summary table, not something Markdoc itself exposes.

## Running it

```bash
node 01_beginner/06_beginner_checkpoint_project/lesson.js
```

## Expected output

```
Converting 2 file(s) from fixtures/ to converted/:

file           | ast nodes | output bytes
---------------|-----------|-------------
article.md     |        20 |          169
hello.md       |        23 |          252

Done. Output written to 01_beginner/06_beginner_checkpoint_project/converted/
```

The `converted/` folder is gitignored, it's regenerated each run.

## Checkpoint

- **The full Beginner-tier pipeline**: `Markdoc.parse` -> (optionally
  parse frontmatter with `js-yaml` into `config.variables`) ->
  `Markdoc.transform` -> `Markdoc.renderers.html`, applied to a whole
  folder instead of one file at a time.
- **`fixtures/partials/` is excluded on purpose**: partial files aren't
  standalone documents, Lesson 11 covers how they get included instead.
- **This is the shape every checkpoint/capstone in this course reuses**:
  a batch converter over `fixtures/`, growing more capable (custom tags,
  validation, config composition) as the course goes on.

You've finished the Beginner tier: parsing, transforming, rendering, and
frontmatter. The Intermediate tier starts with the piece every real
Markdoc document needs next, variables that change what a document
actually says.
