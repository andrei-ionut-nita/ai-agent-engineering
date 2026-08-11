/**
 * Lesson 12: nested tags and slots.
 *
 * Read README.md in this folder first, then read this file top to bottom,
 * then run it with:
 *
 *   node 02_intermediate/12_nested_tags_and_slots/lesson.js
 *
 * A tag's `transform` function can read its own already-transformed
 * children, that's how a parent tag lays out content its child tags
 * produced. This lesson uses fixtures/config-tags.js's `tabs`/`tab` pair
 * ({% tabs %}{% tab title="..." %}...{% /tab %}{% /tabs %}), Markdoc's
 * version of "slots": named children a parent tag arranges.
 */

import Markdoc from "@markdoc/markdoc";
import { tabs, tab } from "../../fixtures/config-tags.js";

function main() {
  console.log("The tabs tag's transform (fixtures/config-tags.js):");
  console.log(`
  transform(node, config) {
    return new Markdoc.Tag("Tabs", {}, node.transformChildren(config));
  }
`);
  console.log(
    "node.transformChildren(config) resolves this tag's children (each " +
      "already run through its own transform) and returns them as a plain " +
      "array, the parent decides what to do with that array, here: just " +
      "pass it straight through as Tabs' own children.",
  );
  console.log();

  const config = { tags: { tabs, tab } };

  const source = `{% tabs %}
{% tab title="npm" %}
Install via \`npm install @markdoc/markdoc\`.
{% /tab %}
{% tab title="yarn" %}
Install via \`yarn add @markdoc/markdoc\`.
{% /tab %}
{% /tabs %}
`;

  const ast = Markdoc.parse(source);
  const renderTree = Markdoc.transform(ast, config);
  const html = Markdoc.renderers.html(renderTree);

  console.log("Render tree, Tabs containing two Tab children:");
  console.log(JSON.stringify(renderTree.children[0], null, 2));
  console.log();
  console.log("HTML:", html);
}

main();
