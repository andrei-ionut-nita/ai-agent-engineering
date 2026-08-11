# Lesson 7: Variables

## The problem: one source document, many contexts

A docs site often needs to render the same page slightly differently
depending on context: a staging banner that shouldn't appear in
production, an SDK name that changes per language tab, a value pulled
from frontmatter (Lesson 5 already used this mechanism without naming it).
Rewriting the source file per context doesn't scale. Markdoc's answer is
**variables**: `{% $name %}` references a value that's resolved at
transform time, not baked into the source.

## The code, piece by piece

```javascript
const SOURCE = `...Environment: {% $env %}...{% if $showBanner %}...{% /if %}...Hello, {% $name %}.`;
```

`{% $env %}`, `{% $showBanner %}`, and `{% $name %}` are all variable
references, the `$` prefix is what marks something as a variable
reference instead of a literal tag name.

```javascript
const ast = Markdoc.parse(SOURCE);
const renderTree = Markdoc.transform(ast, { variables });
```

Parsing happens once and doesn't touch variables at all, `Markdoc.parse`
doesn't know or care that `$env` will later resolve to anything, it just
records "there's a variable reference here." Resolution happens entirely
in `transform`, against whatever `config.variables` you pass, which is
why the same parsed `Ast` can be transformed twice with two different
variable sets and produce two different render trees.

```javascript
renderFor("staging", { env: "staging", showBanner: true, name: "Andrei" });
renderFor("production", { env: "production", showBanner: false, name: "Andrei" });
```

Same source, two calls, two different `config.variables` objects, two
different HTML outputs. In a real site this is how one Markdoc source
file backs multiple environments, locales, or audience segments.

## Running it

```bash
node 02_intermediate/07_variables/lesson.js
```

## Expected output

```
Same source document, parsed once conceptually, transformed twice:

--- staging (variables={"env":"staging","showBanner":true,"name":"Andrei"}) ---
<article><h1>Deploy status</h1><p>Environment: staging</p><p><strong>Warning:</strong> this is a staging environment, data may be reset at any time.</p><p>Hello, Andrei.</p></article>

--- production (variables={"env":"production","showBanner":false,"name":"Andrei"}) ---
<article><h1>Deploy status</h1><p>Environment: production</p><p>Hello, Andrei.</p></article>

Note: {% if $showBanner %} isn't just text substitution, the whole block disappears from the render tree when the variable is falsy, it doesn't render as an empty string, see Lesson 9 for how {% if %} works.
```

## Checkpoint

- **`{% $name %}`**: a variable reference in Markdoc source, resolved
  against `config.variables` at transform time, not parse time.
- **One source, many renders**: the same `Ast` can be transformed
  repeatedly with different `variables`, producing different render
  trees and output each time, no re-parsing needed.
- **`{% if %}` reacts structurally, not textually**: a falsy variable
  makes the guarded block vanish from the render tree entirely, it isn't
  rendered-then-hidden, it's just never added, Lesson 9 covers the
  mechanics.

If anything here still feels unclear, ask before moving to Lesson 8.
