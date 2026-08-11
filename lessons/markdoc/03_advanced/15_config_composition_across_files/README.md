# Lesson 15: Config composition across files

## The problem: one config object, growing forever

Lessons 8-14 each added something to `config`: a function, a couple of
tags, a couple of node overrides. If every lesson (or every section of a
real docs site) kept editing the same giant config object in one file,
that file would become an unreviewable mess fast. Markdoc doesn't need a
special API to solve this, `config` is a plain JavaScript object, so
plain JavaScript module boundaries and object spread are the whole
solution.

## The code, piece by piece

```javascript
import { callout, tabs, tab } from "../../fixtures/config-tags.js";
import { fence, heading } from "../../fixtures/config-nodes.js";
import { uppercase } from "../../fixtures/config-functions.js";
```

Three small, single-purpose modules, each one this course already used
on its own (Lessons 9/12, 14, and 8, respectively). Nothing about them
changes when composed, they're the exact same exports.

```javascript
const config = {
  tags: { callout, tabs, tab },
  nodes: { fence, heading },
  functions: { uppercase },
  variables: { title: "config composition" },
};
```

Composition is just building one object out of several imports, no
`Markdoc.mergeConfig()` or similar exists because none is needed. A real
site organizes this the same way: `config/tags/callout.js`,
`config/tags/tabs.js`, `config/nodes/heading.js`, and one small
`config/index.js` that imports and assembles them, exactly this pattern
at a larger scale.

```javascript
const source = `# {% uppercase($title) %} ... {% callout %} ... {% tabs %}{% tab %}\`\`\`bash ...`;
```

One document exercising all three pieces at once: a function call in the
heading, the validated `callout` tag, nested `tabs`/`tab` tags containing
fenced code blocks that go through the overridden `fence` node, everything
composed together resolves in a single `transform` call, exactly like any
smaller config would.

## Running it

```bash
node 03_advanced/15_config_composition_across_files/lesson.js
```

## Expected output

```
Composed config, sourced from 3 separate fixtures/*.js modules:
  tags:      callout, tabs, tab
  nodes:     fence, heading
  functions: uppercase

Rendered HTML:
<article><h1 id="config-composition">CONFIG COMPOSITION</h1><Callout type="info"><p>This page uses a tag, a node override, and a function, all from separate config modules.</p></Callout><Tabs><Tab title="npm"><pre data-language="bash" data-copyable="true">npm install @markdoc/markdoc
</pre></Tab><Tab title="yarn"><pre data-language="bash" data-copyable="true">yarn add @markdoc/markdoc
</pre></Tab></Tabs></article>
```

## Checkpoint

- **`config` is a plain object**: composing it across files needs no
  Markdoc-specific merge API, ordinary imports and object spread are the
  whole mechanism.
- **Split by concern, not by lesson**: a real project organizes
  `tags/`, `nodes/`, and `functions/` as separate small modules, the same
  shape this course's `fixtures/config-*.js` files already follow.
- **Composed config behaves identically to a hand-written one**: this
  lesson's single `transform` call resolving a function, a tag, nested
  tags, and a node override all at once is proof nothing about
  composition changes Markdoc's runtime behavior.

If anything here still feels unclear, ask before moving to Lesson 16.
