/**
 * Lesson 1: what is Markdoc, and what does its pipeline look like end to end.
 *
 * Read README.md in this folder first, then read this file top to bottom,
 * then run it with:
 *
 *   node 01_beginner/01_what_is_markdoc/lesson.js
 *
 * Markdoc is Stripe's open-source Markdown-based authoring format: regular
 * Markdown, plus tags, variables, and functions, that goes through three
 * distinct stages (parse, transform, render) instead of being turned
 * straight into HTML the way most Markdown libraries work. This lesson
 * doesn't call any Markdoc API yet, it just shows the shape of that
 * pipeline on one tiny string, so the next few lessons can each take one
 * stage and go deeper.
 */

import Markdoc from "@markdoc/markdoc";

const PLAIN_MARKDOWN_MENTAL_MODEL =
  "A typical Markdown library (marked, remark, etc.) does one thing: " +
  "source string in, HTML string out, in a single step you don't control.";

const MARKDOC_MENTAL_MODEL =
  "Markdoc splits that single step into three: parse (source -> Ast), " +
  "transform (Ast + config -> render tree), render (render tree -> HTML, " +
  "React, or anything else you write a renderer for).";

function main() {
  console.log("Plain Markdown, one step:");
  console.log(`  ${PLAIN_MARKDOWN_MENTAL_MODEL}`);
  console.log();
  console.log("Markdoc, three steps:");
  console.log(`  ${MARKDOC_MENTAL_MODEL}`);
  console.log();

  const source = "Hello, **Markdoc**.\n";

  // Stage 1: parse. A string becomes a tree of nodes (the Ast). No config
  // needed yet, parsing doesn't know or care about tags, variables, or
  // functions you plan to use, it just reads Markdoc's syntax.
  const ast = Markdoc.parse(source);

  // Stage 2: transform. The Ast, plus a config object (empty here, later
  // lessons fill it with tags/variables/functions), becomes a render tree,
  // a plain tree of Markdoc.Tag objects and strings, still not HTML.
  const renderTree = Markdoc.transform(ast);

  // Stage 3: render. The render tree becomes a final output format. This
  // course mostly uses the HTML renderer, Lesson 16 uses the React one on
  // the exact same kind of render tree.
  const html = Markdoc.renderers.html(renderTree);

  console.log(`source:      ${JSON.stringify(source)}`);
  console.log(`ast.type:    ${ast.type}`);
  console.log(`renderTree:  ${renderTree.name} tag, ${renderTree.children.length} child(ren)`);
  console.log(`html:        ${html}`);
  console.log();
  console.log("The whole pipeline in one line:");
  console.log("  Markdoc.renderers.html(Markdoc.transform(Markdoc.parse(source)))");
}

main();
