/**
 * Lesson 9: custom tags with the Tag schema.
 *
 * Read README.md in this folder first, then read this file top to bottom,
 * then run it with:
 *
 *   node 02_intermediate/09_custom_tags_with_the_tag_schema/lesson.js
 *
 * Every tag you've used so far ({% if %}, {% $var %} isn't even a tag)
 * is built into Markdoc. This lesson authors a first custom one from
 * scratch: {% callout type="warning" %}...{% /callout %}, defined in
 * fixtures/config-tags.js (reused again in Lessons 12, 15, 18), and
 * shows that a custom tag and a built-in tag share the exact same shape.
 */

import Markdoc from "@markdoc/markdoc";
import { callout } from "../../fixtures/config-tags.js";

function main() {
  console.log("The callout tag's schema (fixtures/config-tags.js):");
  console.log(JSON.stringify(callout, null, 2));
  console.log();

  const config = { tags: { callout } };

  const source = `{% callout type="warning" %}
Double-check your API key before deploying.
{% /callout %}
`;

  const ast = Markdoc.parse(source);
  const renderTree = Markdoc.transform(ast, config);
  console.log("Render tree produced by the custom tag:");
  console.log(JSON.stringify(renderTree, null, 2));
  console.log();
  console.log("HTML:", Markdoc.renderers.html(renderTree));
  console.log();

  // Aside: a built-in tag (`if`) has the exact same schema shape, a
  // `transform` function and/or `attributes`, just shipped with Markdoc
  // instead of authored by you. Custom tags aren't a special case, tags
  // in general are just entries in config.tags, built-in ones are
  // pre-registered defaults.
  console.log("Aside: Markdoc's built-in `if` tag schema, for comparison:");
  console.log(JSON.stringify(Markdoc.tags.if, null, 2));
}

main();
