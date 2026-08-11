# Course index

A linear, one-concept-per-lesson path through **Markdoc**, Stripe's
open-source Markdown-based authoring format: standard Markdown plus tags,
variables, functions, and a schema you can validate before rendering
anything. Do these in order, top to bottom, each lesson folder has a
`README.md` (read first) and a `lesson.js` (run second). Don't move to
the next lesson until the current one's checkpoint questions feel solid.

This is the one course in this repo written in JavaScript, not Python.
Markdoc has no Python port, so its lessons run on Node.js via `node`
instead of `uv run python`. It has no hard prerequisite on any other
course here and can be started cold.

Setup: this course manages its own dependencies with npm, separate from
this project's root `pyproject.toml`/`uv.lock`. If you don't have Node
yet, install the current LTS release from [nodejs.org](https://nodejs.org/),
then confirm it worked with `node --version` (v20 or later) and
`npm --version`. From this course's own folder:

```bash
cd lessons/markdoc
npm install
```

This reads `package.json`/`package-lock.json` and installs
`@markdoc/markdoc` (plus `js-yaml` for frontmatter parsing and `react`
for Lesson 16's React renderer) into a local `node_modules/`, the npm
equivalent of `uv sync`'s `.venv`. No API key or external service is
needed anywhere in this course, every lesson runs locally against the
fixture files in `fixtures/`. Run any lesson from that same folder:

```bash
node <tier>/<NN>_<name>/lesson.js
```

## Beginner: parsing, transforming, and rendering your first Markdoc document

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_markdoc](01_beginner/01_what_is_markdoc/) | What Markdoc is, and how parse -> transform -> render differs from a typical single-step Markdown renderer |
| 02 | [parsing_with_markdoc_parse](01_beginner/02_parsing_with_markdoc_parse/) | `Markdoc.parse()`, the `Ast` node tree, and the `Tokenizer` underneath it |
| 03 | [transform_and_the_render_tree](01_beginner/03_transform_and_the_render_tree/) | `Markdoc.transform()`, the render tree, and how its shape differs from the `Ast` |
| 04 | [rendering_to_html](01_beginner/04_rendering_to_html/) | `Markdoc.renderers.html()`, closing the parse -> transform -> render pipeline |
| 05 | [frontmatter_and_document_metadata](01_beginner/05_frontmatter_and_document_metadata/) | `ast.attributes.frontmatter`, parsing YAML with `js-yaml`, wiring it into `config.variables` |
| 06 | [beginner_checkpoint_project](01_beginner/06_beginner_checkpoint_project/) | **Checkpoint:** convert every file in `fixtures/` to `.html`, with a summary table |

## Intermediate: variables, functions, tags, attributes, validation, partials, nesting

| # | Lesson | Concept |
|---|--------|---------|
| 07 | [variables](02_intermediate/07_variables/) | `{% $variable %}`, rendering one document differently per `config.variables` |
| 08 | [functions](02_intermediate/08_functions/) | `{% function(args) %}`, registering custom functions via `config.functions` |
| 09 | [custom_tags_with_the_tag_schema](02_intermediate/09_custom_tags_with_the_tag_schema/) | Authoring a custom `{% callout %}` tag, and how built-in tags share the same schema shape |
| 10 | [attributes_and_validation](02_intermediate/10_attributes_and_validation/) | Attribute `default`/`matches`, `Markdoc.validate()`, reading structured validation errors |
| 11 | [partials](02_intermediate/11_partials/) | `{% partial file="..." /%}`, `config.partials`, and why Markdoc leaves file resolution to you |
| 12 | [nested_tags_and_slots](02_intermediate/12_nested_tags_and_slots/) | A parent/child tag pair (`{% tabs %}`/`{% tab %}`), `node.transformChildren()` |
| 13 | [intermediate_checkpoint_project](02_intermediate/13_intermediate_checkpoint_project/) | **Checkpoint:** a 3-page doc set with variables, a validated callout, and a partials-based footer |

## Advanced: custom nodes, config composition, React rendering, MDX comparison, capstone

| # | Lesson | Concept |
|---|--------|---------|
| 14 | [custom_nodes_and_overriding_defaults](03_advanced/14_custom_nodes_and_overriding_defaults/) | Overriding built-in `config.nodes` entries (`fence`, `heading`) instead of adding a tag |
| 15 | [config_composition_across_files](03_advanced/15_config_composition_across_files/) | Composing `tags`/`nodes`/`functions` from separate modules with plain object spread |
| 16 | [rendering_to_react](03_advanced/16_rendering_to_react/) | `Markdoc.renderers.react()`, mapping a tag's `render` name to a real React component |
| 17 | [markdoc_vs_mdx](03_advanced/17_markdoc_vs_mdx/) | Markdoc's schema-checked, data-first model vs. MDX's embedded-JSX, code-first model |
| 18 | [advanced_capstone_project](03_advanced/18_advanced_capstone_project/) | **Capstone:** a folder-of-Markdoc-files -> validated -> statically rendered site pipeline, with a generated index |
