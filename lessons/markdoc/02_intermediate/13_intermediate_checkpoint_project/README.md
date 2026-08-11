# Lesson 13: Intermediate checkpoint project

## The problem: prove variables, tags, validation, and partials work together

Lessons 7-12 each covered one mechanism in isolation. Real docs pages
combine several at once: a conditional beta banner (variables + `{% if %}`),
a validated callout (Lesson 9-10's `callout` tag), and a shared footer
(Lesson 11's partials). This checkpoint has no new API, it builds a tiny
3-page doc set using all of them, including one page written to fail
validation on purpose.

## The code, piece by piece

```javascript
const PAGES = {
  "index.md": `... {% if $showBetaBanner %} {% callout type="warning" %}...{% /callout %} {% /if %} ...`,
  "install.md": `... {% callout type="info" %}...{% /callout %} ...`,
  "broken.md": `... {% callout type="urgent" %}...{% /callout %} ...`,
};
```

Three pages: one with a conditional callout gated by a variable, one with
a valid callout, and one (`broken.md`) with a deliberately invalid
`type="urgent"`, matching Lesson 10's validation error exactly, so it
shows up in this lesson's summary instead of being hidden.

```javascript
function buildConfig() {
  const footerAst = Markdoc.parse(footerSource);
  return {
    tags: { callout },
    variables: { showBetaBanner: true },
    partials: { "partials/footer.md": footerAst },
  };
}
```

One config, built once, reused for all three pages, combining Lesson 7's
`variables`, Lesson 9's `tags`, and Lesson 11's `partials` in a single
object, exactly the shape a real site's shared config module would take
(this is also what Lesson 15 splits across multiple files as the config
keeps growing).

```javascript
const errors = Markdoc.validate(ast, config).filter((e) => e.error.level === "error");
```

Validating every page before writing its output, filtered to
`level: "error"` specifically, mirrors a real CI check: warn-level issues
might be acceptable to ship, error-level ones shouldn't be.

## Running it

```bash
node 02_intermediate/13_intermediate_checkpoint_project/lesson.js
```

## Expected output

```
Building 3 page(s):

file          | errors | output bytes
--------------|--------|-------------
index.md      |      0 |          303
install.md    |      0 |          230
broken.md     |      1 |          267
    -> attribute-value-invalid: Attribute 'type' must match one of ["info","warning","error"]. Got 'urgent' instead.

Done. Output written to 02_intermediate/13_intermediate_checkpoint_project/converted/
```

The `converted/` folder is gitignored, it's regenerated each run.

## Checkpoint

- **One shared config, many pages**: variables, tags, and partials all
  live on the same `config` object, built once and reused, the pattern
  every real Markdoc site follows.
- **Validation runs per page, independently of rendering**: a page with
  errors still renders (`broken.md` still produced HTML), but the
  error-count summary is what a CI gate would act on.
- **Partials compose with everything else**: the footer partial renders
  identically on every page regardless of what variables or tags that
  page also used, it's just one more thing `transform` resolves.

You've finished the Intermediate tier: variables, functions, custom tags,
validation, partials, and nesting. The Advanced tier covers overriding
Markdoc's own built-in Markdown rendering, composing configs at scale,
targeting React instead of HTML, and a comparison to MDX.
