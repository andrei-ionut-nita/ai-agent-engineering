# Lesson 14: Custom nodes, overriding Markdoc's built-in defaults

## The problem: sometimes you don't want new syntax, you want different defaults

Custom tags (Lesson 9) add *new* syntax authors have to opt into. But
often what you actually want is for **standard** Markdown, a plain
` ```code``` ` fence or a `#` heading, to render differently everywhere,
without asking every author to learn a new tag. `config.nodes` is for
exactly that: it overrides how Markdoc's own built-in Markdown constructs
transform, keyed by the same names you saw in Lesson 2's `Ast` node types
(`fence`, `heading`, `list`, `paragraph`, ...).

## The code, piece by piece

```javascript
// fixtures/config-nodes.js
export const fence = {
  ...Markdoc.nodes.fence,
  transform(node, config) {
    const attributes = node.transformAttributes(config);
    const children = node.transformChildren(config);
    return new Markdoc.Tag("pre", { ...attributes, "data-copyable": "true" }, children);
  },
};
```

Spreading `...Markdoc.nodes.fence` first keeps its existing `attributes`
schema (`content`, `language`, `process`), then `transform` is fully
replaced: it still builds a `pre` tag the same way the default does, but
adds a `data-copyable="true"` attribute a real UI could use to show a
copy button.

```javascript
export const heading = {
  ...Markdoc.nodes.heading,
  transform(node, config) {
    const children = node.transformChildren(config);
    const id = children.filter(c => typeof c === "string").join(" ")
      .toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
    return new Markdoc.Tag(`h${node.attributes["level"]}`, { ...attributes, id }, children);
  },
};
```

Every heading gets an auto-generated `id` slug (`"Getting Started"` ->
`"getting-started"`) derived from its own text content, useful for
anchor links, without an author ever writing `{% #getting-started %}` by
hand.

```javascript
const config = { nodes: { fence, heading } };
```

Registered under `config.nodes`, not `config.tags`, this is the key
difference from custom tags: `nodes` overrides what already-standard
Markdown syntax produces, `tags` adds syntax that didn't exist before.

## Running it

```bash
node 03_advanced/14_custom_nodes_and_overriding_defaults/lesson.js
```

## Expected output

```
Markdoc's default fence/heading node schemas, for comparison:
  Markdoc.nodes.fence.render:   "pre"
  Markdoc.nodes.heading.render: undefined

This lesson's overrides spread the defaults (...Markdoc.nodes.fence) and replace only `transform`, adding a data-copyable flag to fenced code and an auto-generated `id` slug to headings.

HTML with overridden nodes (note the id= and data-copyable= attributes):
<article><h1 id="getting-started">Getting Started</h1><h2 id="installation">Installation</h2><pre data-language="bash" data-copyable="true">npm install @markdoc/markdoc
</pre></article>

Compare: HTML with the DEFAULT nodes (no config.nodes at all):
<article><h1>Getting Started</h1><h2>Installation</h2><pre data-language="bash">npm install @markdoc/markdoc
</pre></article>
```

## Checkpoint

- **`config.nodes` vs. `config.tags`**: `nodes` overrides how existing
  Markdown constructs (fence, heading, list, ...) render; `tags` adds
  brand-new `{% %}` syntax. Same schema shape (`attributes` +
  `transform`), different purpose.
- **Spread the default, replace what you need**: `{ ...Markdoc.nodes.fence, transform: ... }`
  keeps the built-in `attributes` schema while only changing rendering
  behavior.
- **Site-wide changes without touching every document**: overriding a
  node affects every page automatically, unlike a custom tag, which only
  affects documents whose authors chose to use it.

If anything here still feels unclear, ask before moving to Lesson 15.
