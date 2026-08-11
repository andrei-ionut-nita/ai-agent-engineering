# Lesson 17: Markdoc vs. MDX

## The problem: which one should you actually reach for?

Markdoc isn't the only way to add components to Markdown. [MDX](https://mdxjs.com/)
is the other well-known option: Markdown that can contain literal JSX,
compiled straight into a React component. They look superficially similar
(both let you write `<Callout>` or `{% callout %}` inside a Markdown-ish
file), but they solve the problem very differently, and that difference
matters most around one question: **who is allowed to author content?**

This course doesn't install an MDX compiler (`@mdx-js/mdx`) just for this
comparison, mixing an "arbitrary code execution by design" tool into a
learning repo isn't worth it for one lesson. Instead, this lesson runs a
concrete Markdoc check that has no MDX equivalent, and compares the rest
as a table.

## The code, piece by piece

```javascript
const untrustedInput = `{% callout type="<script>alert(1)</script>" %}\n...`;
const errors = Markdoc.validate(ast, config);
```

This simulates an untrusted author (a CMS contributor, a community PR)
submitting a suspicious-looking attribute value. `Markdoc.validate` never
executes anything, it's a pure data check against `callout`'s `matches`
schema (Lesson 10), and it rejects the value because `"<script>..."` isn't
`"info"`, `"warning"`, or `"error"`, the string is just data, whether or
not it looks like a script tag doesn't matter to the check.

MDX has no equivalent point in its pipeline: an `.mdx` file's embedded
JSX and expressions **are** the content and **are** code, there's no
"validate the data before running anything" step, because there's no
separation between content and code to validate.

## Markdoc vs. MDX

| Aspect | Markdoc | MDX |
|---|---|---|
| Output shape | Data: a plain render tree (`Tag` objects + strings) | Code: a compiled React component, arbitrary JS included |
| Untrusted authors | Safe by default, tags are schema-checked, no arbitrary JS execution | Risky, embedded JSX/expressions run as real code at build/render time |
| Validation before render | Yes, `Markdoc.validate()` checks attributes/structure with zero execution | No built-in equivalent, invalid JSX is a compile error, not a content error |
| Multiple output targets | Yes, same render tree to HTML (Lesson 4) or React (Lesson 16) | No, MDX compiles straight to one target (usually a React/JS component) |
| Learning curve | A small tag/attribute syntax on top of Markdown | Markdown syntax plus real JSX/JS knowledge to author pages |

Neither is strictly better. If every author on a docs site is a trusted
engineer who wants full component power and doesn't mind coupling content
to React specifically, MDX's directness is a real advantage. If content
comes from many authors, non-engineers, a CMS, or community
contributions, and you want to validate or target multiple output formats
from one source, Markdoc's schema-checked, data-first design is the
better fit, which is exactly why Stripe (many external doc contributors,
strict review requirements) built and uses it.

## Running it

```bash
node 03_advanced/17_markdoc_vs_mdx/lesson.js
```

## Expected output

```
An untrusted-author-shaped input, validated with Markdoc's schema:
  input:  "{% callout type=\"<script>alert(1)</script>\" %}"
  errors: 1
    attribute-value-invalid: Attribute 'type' must match one of ["info","warning","error"]. Got '<script>alert(1)</script>' instead.
  -> rejected as bad DATA (an attribute value outside the schema's `matches` list), nothing was ever executed to reach that verdict.

MDX has no equivalent check: an author could write a literal <script> tag, or arbitrary {jsExpression()} directly in an .mdx file, and it becomes real, executable output at build time, there's no schema step to catch it first.

Markdoc vs. MDX:

  aspect                   | Markdoc                                                 | MDX
  Output shape             | Data: a plain render tree (Tag objects + strings)       | Code: a compiled React component, arbitrary JS included
  Untrusted authors        | Safe by default, tags are schema-checked, no arbitrary JS execution | Risky, embedded JSX/expressions run as real code at build/render time
  Validation before render | Yes, Markdoc.validate() checks attributes/structure with zero execution | No built-in equivalent, invalid JSX is a compile error, not a content error
  Multiple output targets  | Yes, same render tree to HTML (Lesson 4) or React (Lesson 16) | No, MDX compiles straight to one target (usually a React/JS component)
  Learning curve           | A small tag/attribute syntax on top of Markdown         | Markdown syntax plus real JSX/JS knowledge to author pages
```

## Checkpoint

- **Markdoc is data, MDX is code**: a Markdoc render tree is inspectable,
  serializable, and safe to build from untrusted input; MDX compiles
  content directly into executable JavaScript.
- **Validation is Markdoc's structural advantage**: `Markdoc.validate()`
  catches bad content before render, with zero code execution, MDX has
  no equivalent, because there's no content/code separation to check.
- **Choose based on who authors the content**: many/untrusted/
  non-engineer authors favor Markdoc; a small trusted engineering team
  wanting full component power favors MDX.

If anything here still feels unclear, ask before moving to Lesson 18,
this course's capstone project.
