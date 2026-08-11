# Lesson 9: Custom tags with the `Tag` schema

## The problem: `{% if %}` and `{% table %}` aren't special, they're just tags

Every built-in tag Markdoc ships (`if`, `else`, `table`, `partial`, `slot`)
is defined the exact same way you'd define your own: an object registered
in `config.tags`, with a `render` name (or a `transform` function) and an
`attributes` schema. This lesson authors a first custom tag, `{% callout %}`,
and then looks at a built-in tag's schema right after, to make that
equivalence concrete.

## The code, piece by piece

```javascript
// fixtures/config-tags.js
export const callout = {
  render: "Callout",
  attributes: {
    type: { type: String, default: "info", matches: ["info", "warning", "error"] },
  },
};
```

`render: "Callout"` is just a string label, it doesn't create an HTML
`<Callout>` element by magic, the HTML renderer literally writes
`<Callout ...>` as a tag name (visible in this lesson's output), it's the
*consuming* renderer's job to decide what "Callout" means, a React
renderer (Lesson 16) can map that same string to an actual component.

```javascript
const config = { tags: { callout } };
const ast = Markdoc.parse(source);
const renderTree = Markdoc.transform(ast, config);
```

Registering the tag under `config.tags.callout` is what makes
`{% callout type="warning" %}...{% /callout %}` resolve to a `Tag` node
instead of erroring or being left as literal text. The tag's `attributes`
schema (`type`, defaulting to `"info"`) is what fills in
`renderTree`'s `attributes: { "type": "warning" }`.

```javascript
console.log(JSON.stringify(Markdoc.tags.if, null, 2));
```

`Markdoc.tags.if` is Markdoc's actual built-in schema object for
`{% if %}`, exported for inspection. It's an `attributes`-only schema
(no `render`, `if` doesn't produce a wrapper element, it conditionally
includes or excludes its children, that's Lesson 7's `{% if $showBanner %}`
behavior explained). The shape, an object with `attributes` and/or
`transform`, is identical to `callout`'s, custom and built-in tags are
the same mechanism.

## Running it

```bash
node 02_intermediate/09_custom_tags_with_the_tag_schema/lesson.js
```

## Expected output

```
The callout tag's schema (fixtures/config-tags.js):
{
  "render": "Callout",
  "attributes": {
    "type": {
      "default": "info",
      "matches": [
        "info",
        "warning",
        "error"
      ]
    }
  }
}

Render tree produced by the custom tag:
{
  "$$mdtype": "Tag",
  "name": "article",
  "attributes": {},
  "children": [
    {
      "$$mdtype": "Tag",
      "name": "Callout",
      "attributes": {
        "type": "warning"
      },
      "children": [
        {
          "$$mdtype": "Tag",
          "name": "p",
          "attributes": {},
          "children": [
            "Double-check your API key before deploying."
          ]
        }
      ]
    }
  ]
}

HTML: <article><Callout type="warning"><p>Double-check your API key before deploying.</p></Callout></article>

Aside: Markdoc's built-in `if` tag schema, for comparison:
{
  "attributes": {
    "primary": {
      "render": false
    }
  }
}
```

(The `type: String` field on `callout`'s attribute schema doesn't appear
in the printed JSON, `JSON.stringify` silently drops function/class
values, `String` is a constructor function, this is a JSON quirk, not a
Markdoc one.)

## Checkpoint

- **A tag is `{ render?, attributes?, transform? }`**: register it under
  `config.tags.<name>`, use it from source as `{% <name> attr="..." %}`.
- **`render` is just a label**: it becomes the render tree node's `.name`,
  what that name *means* is entirely up to the renderer consuming the
  tree, not something the tag definition controls.
- **Built-in tags aren't special-cased**: `Markdoc.tags.if`,
  `Markdoc.tags.table`, etc. use the exact same schema shape as any
  custom tag you write, they're just pre-registered.

If anything here still feels unclear, ask before moving to Lesson 10.
