# Lesson 10: Attributes and validation

## The problem: a wrong attribute value shouldn't ship silently

Lesson 9's `callout` tag restricts `type` to `"info" | "warning" | "error"`
via `matches`. But nothing stops someone writing `{% callout type="urgent" %}`
in a doc, and `transform()` alone won't catch it, it just renders whatever
attribute value it's given. Markdoc separates *checking* a document from
*rendering* it: `Markdoc.validate(ast, config)` runs the schema checks
without producing any output, exactly the kind of check you'd wire into
CI before a docs deploy.

## The code, piece by piece

```javascript
const validErrors = Markdoc.validate(validAst, config);
```

`Markdoc.validate` takes the same `ast` + `config` shape `transform` does,
but returns an array of structured error objects instead of a render
tree, an empty array means the document passed every check the tag
schemas describe.

```javascript
for (const error of invalidErrors) {
  console.log(error.error.id, error.error.level, error.error.message);
}
```

Each validation error carries `.error.id` (a stable, matchable code like
`"attribute-value-invalid"`), `.error.level` (`"error"` vs. lower
severities Markdoc also supports, like warnings), and `.error.message`
(human-readable). The `matches` list on `callout`'s `type` attribute
(from Lesson 9's `fixtures/config-tags.js`) is exactly what produces this
specific error when the value isn't `"info"`, `"warning"`, or `"error"`.

## Running it

```bash
node 02_intermediate/10_attributes_and_validation/lesson.js
```

## Expected output

```
Validating a correct document:
  errors found: 0

Validating a broken document (type="urgent", not in the schema's `matches` list):
  errors found: 1
    id: attribute-value-invalid
    level: error
    message: Attribute 'type' must match one of ["info","warning","error"]. Got 'urgent' instead.

Validation is a separate step from rendering, transform() would still happily render the invalid document (it just keeps the attribute value as-is), validate() is what catches the mistake before anything ships.
```

## Checkpoint

- **`Markdoc.validate(ast, config)`**: runs the same tag/attribute
  schemas `transform` uses, but only to check, no render tree is
  produced, an empty array means the document is valid.
- **Errors are structured, not just strings**: `.error.id`, `.error.level`,
  `.error.message`, meant to be matched programmatically (e.g. failing a
  CI check on any `level: "error"` entry), not just printed.
- **Validation and rendering are independent**: `transform()` doesn't
  validate anything on its own, an invalid document still renders,
  `validate()` is a separate, explicit step you choose to run.

If anything here still feels unclear, ask before moving to Lesson 11.
