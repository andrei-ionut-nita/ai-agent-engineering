/**
 * Lesson 4: rendering a render tree to HTML.
 *
 * Read README.md in this folder first, then read this file top to bottom,
 * then run it with:
 *
 *   node 01_beginner/04_rendering_to_html/lesson.js
 *
 * Markdoc.renderers.html() is the third and final stage: render tree in,
 * an HTML string out. This lesson closes the full pipeline end to end on
 * the fixtures/hello.md file used in Lessons 2 and 3, then shows that the
 * HTML renderer only needs a render tree, it doesn't need the Ast or the
 * original source string at all.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Markdoc from "@markdoc/markdoc";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = path.join(__dirname, "..", "..", "fixtures");

function main() {
  const source = fs.readFileSync(path.join(FIXTURES_DIR, "hello.md"), "utf8");

  // Stage 1 + 2, same as Lessons 2 and 3.
  const ast = Markdoc.parse(source);
  const renderTree = Markdoc.transform(ast, {});

  // Stage 3: render. This is the only stage that produces a final,
  // consumable output. Everything before this point is Markdoc's own
  // internal representation.
  const html = Markdoc.renderers.html(renderTree);

  console.log("Final HTML:");
  console.log(html);
  console.log();

  // The renderer only looks at the render tree, proof: build a render
  // tree entirely by hand (no parse, no transform, no source string) and
  // render that instead.
  const handBuiltTree = new Markdoc.Tag("article", {}, [
    new Markdoc.Tag("h1", {}, ["Built without parsing anything"]),
    new Markdoc.Tag("p", {}, ["This render tree was constructed directly in JavaScript."]),
  ]);
  console.log("Rendering a hand-built render tree (no source string involved):");
  console.log(Markdoc.renderers.html(handBuiltTree));
}

main();
