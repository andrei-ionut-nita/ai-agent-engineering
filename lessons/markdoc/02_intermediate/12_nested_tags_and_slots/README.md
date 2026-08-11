# Lesson 12: Nested tags and slots

## The problem: a parent tag needs to arrange its children's output

A tabs component, a numbered-steps list, an accordion, all of these are
one parent tag wrapping several child tags, where the parent needs to
know what each child produced in order to lay them out (a tab title, a
step number). Markdoc doesn't have a separate "slots" API for this, a
parent tag's `transform` function just reads `node.transformChildren()`,
the already-transformed results of its own children.

## The code, piece by piece

```javascript
// fixtures/config-tags.js
export const tabs = {
  render: "Tabs",
  transform(node, config) {
    return new Markdoc.Tag("Tabs", {}, node.transformChildren(config));
  },
};
```

`node.transformChildren(config)` runs `transform` on every child node
(each child's own `transform`, in this case `tab`'s) and returns the
results as a plain array. `tabs` itself does almost nothing with that
array here beyond passing it straight through, but it could just as
easily filter, reorder, or wrap individual children, "slots" in other
templating systems are just this: a parent function deciding what to do
with its children's outputs.

```javascript
export const tab = {
  render: "Tab",
  attributes: { title: { type: String, required: true } },
  transform(node, config) {
    const attributes = node.transformAttributes(config);
    return new Markdoc.Tag("Tab", attributes, node.transformChildren(config));
  },
};
```

`tab` is a normal tag on its own, nothing marks it as "only valid inside
`tabs`", nesting here is purely a source-syntax convention (you write one
inside the other), not something Markdoc enforces structurally. Each
`tab`'s `title` attribute survives into the render tree via
`node.transformAttributes(config)`, which is how the parent `Tabs`
component (in a real UI) would know what label to show for each child.

## Running it

```bash
node 02_intermediate/12_nested_tags_and_slots/lesson.js
```

## Expected output

```
The tabs tag's transform (fixtures/config-tags.js):

  transform(node, config) {
    return new Markdoc.Tag("Tabs", {}, node.transformChildren(config));
  }

node.transformChildren(config) resolves this tag's children (each already run through its own transform) and returns them as a plain array, the parent decides what to do with that array, here: just pass it straight through as Tabs' own children.

Render tree, Tabs containing two Tab children:
{
  "$$mdtype": "Tag",
  "name": "Tabs",
  "attributes": {},
  "children": [
    {
      "$$mdtype": "Tag",
      "name": "Tab",
      "attributes": { "title": "npm" },
      "children": [
        {
          "$$mdtype": "Tag",
          "name": "p",
          "attributes": {},
          "children": [
            "Install via ",
            { "$$mdtype": "Tag", "name": "code", "attributes": {}, "children": ["npm install @markdoc/markdoc"] },
            "."
          ]
        }
      ]
    },
    {
      "$$mdtype": "Tag",
      "name": "Tab",
      "attributes": { "title": "yarn" },
      "children": [
        {
          "$$mdtype": "Tag",
          "name": "p",
          "attributes": {},
          "children": [
            "Install via ",
            { "$$mdtype": "Tag", "name": "code", "attributes": {}, "children": ["yarn add @markdoc/markdoc"] },
            "."
          ]
        }
      ]
    }
  ]
}

HTML: <article><Tabs><Tab title="npm"><p>Install via <code>npm install @markdoc/markdoc</code>.</p></Tab><Tab title="yarn"><p>Install via <code>yarn add @markdoc/markdoc</code>.</p></Tab></Tabs></article>
```

## Checkpoint

- **`node.transformChildren(config)`**: a parent tag's way of reading its
  own already-transformed children, the mechanism behind any nested-tag
  layout (tabs, steps, accordions).
- **Nesting is a source-syntax convention, not an enforced structure**:
  Markdoc doesn't stop you writing `{% tab %}` outside `{% tabs %}`,
  the parent-child relationship exists because of how the source is
  written and how the parent's `transform` chooses to use its children,
  not because of a schema rule.
- **Child attributes flow up naturally**: `tab`'s `title` attribute ends
  up in the render tree exactly like any tag's attributes, letting a real
  UI renderer read it back out to build tab labels.

If anything here still feels unclear, ask before moving to Lesson 13,
this tier's checkpoint project.
