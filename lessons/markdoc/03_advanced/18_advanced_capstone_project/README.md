# Lesson 18: Advanced capstone project

## The problem: put the whole pipeline together, the way a real site would

This capstone has no new Markdoc API. It's every piece from this course
assembled into one small content pipeline: frontmatter-driven pages
(Lesson 5), a composed config with custom tags, node overrides, functions,
and partials (Lesson 15), validation that rejects bad pages instead of
silently publishing them (Lesson 10), and a generated site index, the
shape of a real static-site build script.

## The code, piece by piece

```javascript
const config = { ...baseConfig, variables: { frontmatter } };
const errors = Markdoc.validate(ast, config).filter((e) => e.error.level === "error");
if (errors.length > 0) {
  console.log(`FAIL  ${filename}: ...`);
  rejected.push(filename);
  continue;
}
```

Each page gets its own `config.variables.frontmatter`, layered on top of
the shared `baseConfig` (tags, nodes, functions, partials, built once).
Validation runs **before** any write happens, `broken.md`'s invalid
`callout` type fails here and the loop moves on without ever calling
`transform` or `renderers.html` on it, "fail loudly, don't publish"
instead of shipping broken output.

```javascript
const renderTree = Markdoc.transform(ast, config);
const html = Markdoc.renderers.html(renderTree);
fs.writeFileSync(path.join(OUTPUT_DIR, outputName), html);
published.push({ outputName, title: frontmatter.title });
```

Only pages that passed validation reach this point, so `published` ends
up as an accurate list of what's actually safe to link to.

```javascript
const indexLinks = published
  .filter((page) => page.outputName !== "index.html")
  .map((page) => `<li><a href="${page.outputName}">${page.title}</a></li>`)
  .join("");
const indexHtml = `<article><h1>Site index</h1><ul>${indexLinks}</ul></article>`;
```

The generated `index.html` links every *other* published page (excluding
itself), built by hand as plain string HTML, this part isn't a Markdoc
document, it's ordinary site-scaffolding code, the same kind you'd write
around any static site generator regardless of what authoring format
feeds it.

## Running it

```bash
node 03_advanced/18_advanced_capstone_project/lesson.js
```

## Expected output

```
Building 4 page(s):

OK    index.md -> index.html (title: "Markdoc Course Site")
OK    install.md -> install.html (title: "Installation")
OK    usage.md -> usage.html (title: "Usage")
FAIL  broken.md: 1 validation error(s), not published
        attribute-value-invalid: Attribute 'type' must match one of ["info","warning","error"]. Got 'not-a-real-type' instead.

Published: 3, rejected: 1
Output written to 03_advanced/18_advanced_capstone_project/converted/, including a generated index.html
```

The `converted/` folder is gitignored, it's regenerated each run.

## Checkpoint

- **The full pipeline, end to end**: frontmatter -> composed config
  (tags, nodes, functions, partials) -> validate -> transform -> render,
  applied per file, over a whole content folder.
- **Validation gates publishing**: this course's earlier lessons ran
  `Markdoc.validate` and inspected the result; this capstone actually
  acts on it, a failed page never reaches `transform`, matching how a
  real CI pipeline would block a broken docs page from shipping.
- **The render tree pipeline is reusable at any scale**: nothing about
  this capstone's per-page logic differs from Lesson 1's three-call
  pipeline, it's the same `parse` -> `transform` -> `render`, just looped
  over more files with a richer config.

You've finished the Markdoc course: parsing, transforming, rendering,
frontmatter, variables, functions, custom tags, validation, partials,
nested tags, node overrides, config composition, the React renderer, and
how Markdoc compares to MDX. If you want to go further from here, Markdoc's
own docs at [markdoc.dev](https://markdoc.dev/) cover advanced schema
patterns (like custom attribute `type` validators) this course didn't
need for its examples.
