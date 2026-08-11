# Lesson 8: Functions

## The problem: sometimes a value needs to be computed, not just looked up

Variables (Lesson 7) give you a value as-is. Sometimes you need a
*transformation* of a value: uppercase a title, format a date, repeat a
string, pick a plural form. Markdoc's **functions** cover that: registered
in `config.functions`, called from source as `{% functionName(args) %}`.

## The code, piece by piece

```javascript
import { uppercase } from "../../fixtures/config-functions.js";
```

`fixtures/config-functions.js` defines `uppercase` once so it can be
reused here and again in Lesson 15's config composition, instead of
redefining the same tiny function in every lesson that needs it.

```javascript
const repeat = {
  transform(parameters) {
    const [text, count] = Object.values(parameters);
    return String(text).repeat(Number(count));
  },
};
```

A function is an object with a `transform(parameters)` method. `parameters`
arrives as an **object keyed by position** (`{"0": ..., "1": ...}`), not a
true array, `Object.values(parameters)` turns it into an ordinary array
you can destructure, matching the order arguments were written in source:
`{% repeat($divider, 20) %}` becomes `parameters = {"0": "-", "1": 20}`.

```javascript
const config = { functions: { uppercase, repeat }, variables: { title: "shipping update", divider: "-" } };
```

Functions are registered the same way tags and variables are, one more
key on the `config` object passed to `transform`.

```
# {% uppercase($title) %}
```

The call resolves `$title` to `"shipping update"` first (variable
resolution happens before the function runs), then passes that resolved
string into `uppercase()`, functions never see the literal text `"$title"`,
only its resolved value, which is why the same source line's literal text
`"$title"` (written without `{% %}` later in this lesson's fixture) shows
up unresolved in the output, it was never inside a tag delimiter to begin
with.

## Running it

```bash
node 02_intermediate/08_functions/lesson.js
```

## Expected output

```
Config functions registered: [ 'uppercase', 'repeat' ]

Rendered HTML:
<article><h1>SHIPPING UPDATE</h1>--------------------<p>Functions receive already-resolved values, SHIPPING UPDATE first resolves $title to &quot;shipping update&quot;, then calls uppercase() with that string, functions never see the literal text &quot;$title&quot;.</p></article>
```

## Checkpoint

- **`{% functionName(args) %}`**: calls a function registered on
  `config.functions`, resolved at transform time, same as tags and
  variables.
- **`parameters` is position-keyed, not a real array**: use
  `Object.values(parameters)` (or index by `parameters[0]`,
  `parameters[1]`, ...) to work with function arguments.
- **Arguments resolve before the function runs**: `{% uppercase($title) %}`
  calls `uppercase()` with `$title`'s already-resolved value, never the
  literal variable reference text.

If anything here still feels unclear, ask before moving to Lesson 9.
