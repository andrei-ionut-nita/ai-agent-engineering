/**
 * Lesson 7: variables.
 *
 * Read README.md in this folder first, then read this file top to bottom,
 * then run it with:
 *
 *   node 02_intermediate/07_variables/lesson.js
 *
 * {% $name %} in a Markdoc source string is a variable reference. It
 * resolves against config.variables at transform time, not parse time,
 * which means the same source document can render differently depending
 * on what variables you pass in. This lesson renders one document twice,
 * once per "environment", to make that concrete.
 */

import Markdoc from "@markdoc/markdoc";

const SOURCE = `# Deploy status

Environment: {% $env %}

{% if $showBanner %}
**Warning:** this is a staging environment, data may be reset at any time.
{% /if %}

Hello, {% $name %}.
`;

function renderFor(label, variables) {
  const ast = Markdoc.parse(SOURCE);
  const renderTree = Markdoc.transform(ast, { variables });
  const html = Markdoc.renderers.html(renderTree);
  console.log(`--- ${label} (variables=${JSON.stringify(variables)}) ---`);
  console.log(html);
  console.log();
}

function main() {
  console.log("Same source document, parsed once conceptually, transformed twice:");
  console.log();

  renderFor("staging", { env: "staging", showBanner: true, name: "Andrei" });
  renderFor("production", { env: "production", showBanner: false, name: "Andrei" });

  console.log(
    "Note: {% if $showBanner %} isn't just text substitution, the whole " +
      "block disappears from the render tree when the variable is falsy, " +
      "it doesn't render as an empty string, see Lesson 9 for how {% if %} works.",
  );
}

main();
