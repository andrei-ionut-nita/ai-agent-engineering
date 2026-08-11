/**
 * Lesson 14: custom nodes, overriding Markdoc's built-in defaults.
 *
 * Read README.md in this folder first, then read this file top to bottom,
 * then run it with:
 *
 *   node 03_advanced/14_custom_nodes_and_overriding_defaults/lesson.js
 *
 * `config.tags` adds new syntax. `config.nodes` changes how *standard*
 * Markdown constructs (fence, heading, list, ...) render, without
 * inventing any new {% %} syntax. This lesson overrides `fence` (fenced
 * code blocks) and `heading`, both defined once in
 * fixtures/config-nodes.js (reused again in Lesson 15).
 */

import Markdoc from "@markdoc/markdoc";
import { fence, heading } from "../../fixtures/config-nodes.js";

function main() {
  console.log("Markdoc's default fence/heading node schemas, for comparison:");
  console.log(`  Markdoc.nodes.fence.render:   ${JSON.stringify(Markdoc.nodes.fence.render)}`);
  console.log(`  Markdoc.nodes.heading.render: ${JSON.stringify(Markdoc.nodes.heading.render)}`);
  console.log();
  console.log(
    "This lesson's overrides spread the defaults (...Markdoc.nodes.fence) " +
      "and replace only `transform`, adding a data-copyable flag to fenced " +
      "code and an auto-generated `id` slug to headings.",
  );
  console.log();

  const config = { nodes: { fence, heading } };

  const source = `# Getting Started

## Installation

\`\`\`bash
npm install @markdoc/markdoc
\`\`\`
`;

  const ast = Markdoc.parse(source);
  const renderTree = Markdoc.transform(ast, config);
  const html = Markdoc.renderers.html(renderTree);

  console.log("HTML with overridden nodes (note the id= and data-copyable= attributes):");
  console.log(html);
  console.log();

  console.log("Compare: HTML with the DEFAULT nodes (no config.nodes at all):");
  console.log(Markdoc.renderers.html(Markdoc.transform(ast, {})));
}

main();
