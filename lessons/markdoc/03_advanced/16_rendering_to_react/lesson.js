/**
 * Lesson 16: rendering to React.
 *
 * Read README.md in this folder first, then read this file top to bottom,
 * then run it with:
 *
 *   node 03_advanced/16_rendering_to_react/lesson.js
 *
 * The same render tree Lesson 4 fed to Markdoc.renderers.html can go to
 * Markdoc.renderers.react instead, producing React elements. This lesson
 * maps the callout tag's render: "Callout" string to a real React
 * component and inspects the resulting element tree with console.log,
 * no bundler or JSX toolchain needed, just the react package as a
 * runtime dependency.
 */

import Markdoc from "@markdoc/markdoc";
import React from "react";
import { callout } from "../../fixtures/config-tags.js";

// A real component. It takes the props the render tree's Callout tag
// attributes become, `type`, plus `children`, and would normally return
// JSX, written here with React.createElement since this lesson has no
// JSX compiler in its toolchain.
function Callout({ type, children }) {
  return React.createElement("div", { className: `callout callout-${type}` }, children);
}

function main() {
  const config = { tags: { callout } };
  const source = `{% callout type="warning" %}\nDouble-check your API key.\n{% /callout %}\n`;

  const ast = Markdoc.parse(source);
  const renderTree = Markdoc.transform(ast, config);

  // Same render tree as every other lesson, different renderer. The HTML
  // renderer (Lesson 4) and this one both walk the exact same tree shape.
  const html = Markdoc.renderers.html(renderTree);
  console.log("HTML renderer output (Lesson 4's renderer, for comparison):");
  console.log(`  ${html}`);
  console.log();

  // Markdoc.renderers.react needs to know which component "Callout"
  // (the render tree's tag name) actually maps to, that's the
  // components map.
  const element = Markdoc.renderers.react(renderTree, React, {
    components: { Callout },
  });

  console.log("React renderer output, a real React element tree (not mounted, just inspected):");
  console.log(`  element.type:                                ${element.type}`);
  console.log(`  element.props.children.type.name:             ${element.props.children.type.name}`);
  console.log(`  element.props.children.props.type:            ${JSON.stringify(element.props.children.props.type)}`);
  console.log(`  element.props.children.props.children.type:   ${element.props.children.props.children.type}`);
  console.log();
  console.log(
    "element.props.children is the Callout element itself (React function " +
      "component reference, not a string), proof the render tree's " +
      "\"Callout\" name resolved to the actual Callout() function above.",
  );
}

main();
