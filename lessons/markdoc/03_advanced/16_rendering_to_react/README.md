# Lesson 16: Rendering to React

## The problem: HTML strings aren't always what you want

Lesson 4's `Markdoc.renderers.html` produces a plain string, great for a
static site, less useful if your docs live inside a React app where a
`Callout` should be an actual interactive component, not a `<Callout>`
string tag a browser doesn't understand. `Markdoc.renderers.react` solves
this: same render tree in, real React elements out.

## The code, piece by piece

```javascript
function Callout({ type, children }) {
  return React.createElement("div", { className: `callout callout-${type}` }, children);
}
```

An ordinary React function component. Written with `React.createElement`
instead of JSX because this course's lessons run directly with `node`,
no build step or JSX compiler, JSX is just syntax sugar for exactly this
call anyway.

```javascript
const element = Markdoc.renderers.react(renderTree, React, {
  components: { Callout },
});
```

This is the piece that closes the loop from Lesson 9: `callout`'s tag
schema set `render: "Callout"`, a plain string. The React renderer's
`components` map is what turns that string into the actual `Callout`
function reference, `element.props.children.type` (below) is a real
function, not the string `"Callout"`.

```javascript
console.log(element.props.children.type.name); // "Callout"
```

Rather than mounting the element in a browser (out of scope for a
`node`-run lesson), this just walks the returned element tree with
`console.log`, `element` is a real React element object
(`$$typeof: Symbol(react.element)`), the same kind of value `React.createElement`
or JSX would produce, `Markdoc.renderers.react` just built it from a
render tree instead of hand-written JSX.

## Running it

```bash
node 03_advanced/16_rendering_to_react/lesson.js
```

## Expected output

```
HTML renderer output (Lesson 4's renderer, for comparison):
  <article><Callout type="warning"><p>Double-check your API key.</p></Callout></article>

React renderer output, a real React element tree (not mounted, just inspected):
  element.type:                                article
  element.props.children.type.name:             Callout
  element.props.children.props.type:            "warning"
  element.props.children.props.children.type:   p

element.props.children is the Callout element itself (React function component reference, not a string), proof the render tree's "Callout" name resolved to the actual Callout() function above.
```

## Checkpoint

- **`Markdoc.renderers.react(renderTree, React, { components })`**: the
  same render tree the HTML renderer consumes, targeted at React instead,
  no re-parsing or re-transforming needed.
- **`components` maps render tree tag names to real components**: a tag's
  `render: "Callout"` string (Lesson 9) only becomes a mounted
  `<Callout>` once a renderer's `components` map says what "Callout"
  means, HTML and React interpret that same string differently.
- **The render tree is the actual portability layer**: this is the
  concrete payoff of splitting parse/transform/render into separate
  stages back in Lesson 1, one transformed document, multiple possible
  output formats.

If anything here still feels unclear, ask before moving to Lesson 17.
