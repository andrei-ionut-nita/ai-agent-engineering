/**
 * Lesson 3: Markdoc.transform and the render tree.
 *
 * Read README.md in this folder first, then read this file top to bottom,
 * then run it with:
 *
 *   node 01_beginner/03_transform_and_the_render_tree/lesson.js
 *
 * transform() is the middle stage of the pipeline: it takes the Ast from
 * Lesson 2 and a config object, and produces a render tree, plain
 * Markdoc.Tag objects and strings. This lesson parses the same fixture as
 * Lesson 2, transforms it, and compares the two tree shapes directly.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Markdoc from "@markdoc/markdoc";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = path.join(__dirname, "..", "..", "fixtures");

function describeRenderNode(node, depth = 0) {
  const indent = "  ".repeat(depth);
  if (typeof node === "string") {
    console.log(`${indent}"${node}"`);
    return;
  }
  const attrs = Object.keys(node.attributes).length
    ? ` attributes=${JSON.stringify(node.attributes)}`
    : "";
  console.log(`${indent}<${node.name}>${attrs}`);
  for (const child of node.children) {
    describeRenderNode(child, depth + 1);
  }
}

function main() {
  const source = fs.readFileSync(path.join(FIXTURES_DIR, "hello.md"), "utf8");

  const ast = Markdoc.parse(source);
  console.log(`Ast (Lesson 2's shape): root type "${ast.type}", nodes carry .type + .attributes`);
  console.log();

  // transform() is a pure function: Ast + config -> render tree. Passing
  // {} here (no tags/variables/functions yet) still runs the full
  // pipeline, plain Markdown constructs become their built-in Tag
  // equivalents (heading -> h1, paragraph -> p, list -> ul) on their own.
  const renderTree = Markdoc.transform(ast, {});
  console.log(`Render tree (this lesson's shape): root tag "<${renderTree.name}>", nodes carry .name + .attributes + .children`);
  console.log();
  console.log("Render tree, walked:");
  describeRenderNode(renderTree);

  console.log();
  console.log("Ast node types vs render tree tag names for the same content:");
  console.log("  Ast 'heading' (attributes.level=1)  ->  render tree tag 'h1'");
  console.log("  Ast 'paragraph'                     ->  render tree tag 'p'");
  console.log("  Ast 'list' (attributes.ordered=false) -> render tree tag 'ul'");
  console.log("  Ast 'item'                          ->  render tree tag 'li'");
}

main();
