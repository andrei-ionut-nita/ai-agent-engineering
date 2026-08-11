/**
 * Lesson 15: config composition across files.
 *
 * Read README.md in this folder first, then read this file top to bottom,
 * then run it with:
 *
 *   node 03_advanced/15_config_composition_across_files/lesson.js
 *
 * By this point the course has accumulated tags (Lesson 9, 12), node
 * overrides (Lesson 14), and functions (Lesson 8), each in its own
 * fixtures/*.js module. Real docs sites keep growing this way: a shared
 * base config plus per-section additions, composed with plain object
 * spread rather than one file that keeps growing forever. This lesson
 * composes all of them into a single config and renders one document
 * that uses every piece at once.
 */

import Markdoc from "@markdoc/markdoc";
import { callout, tabs, tab } from "../../fixtures/config-tags.js";
import { fence, heading } from "../../fixtures/config-nodes.js";
import { uppercase } from "../../fixtures/config-functions.js";

function main() {
  // Each import is a small, single-purpose module. Composition is just
  // object spread, no special Markdoc "merge configs" API exists,
  // because config is a plain JS object, plain JS tools compose it.
  const config = {
    tags: { callout, tabs, tab },
    nodes: { fence, heading },
    functions: { uppercase },
    variables: { title: "config composition" },
  };

  console.log("Composed config, sourced from 3 separate fixtures/*.js modules:");
  console.log(`  tags:      ${Object.keys(config.tags).join(", ")}`);
  console.log(`  nodes:     ${Object.keys(config.nodes).join(", ")}`);
  console.log(`  functions: ${Object.keys(config.functions).join(", ")}`);
  console.log();

  const source = `# {% uppercase($title) %}

{% callout type="info" %}
This page uses a tag, a node override, and a function, all from separate config modules.
{% /callout %}

{% tabs %}
{% tab title="npm" %}
\`\`\`bash
npm install @markdoc/markdoc
\`\`\`
{% /tab %}
{% tab title="yarn" %}
\`\`\`bash
yarn add @markdoc/markdoc
\`\`\`
{% /tab %}
{% /tabs %}
`;

  const ast = Markdoc.parse(source);
  const renderTree = Markdoc.transform(ast, config);
  const html = Markdoc.renderers.html(renderTree);

  console.log("Rendered HTML:");
  console.log(html);
}

main();
