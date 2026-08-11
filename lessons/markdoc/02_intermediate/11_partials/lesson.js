/**
 * Lesson 11: partials.
 *
 * Read README.md in this folder first, then read this file top to bottom,
 * then run it with:
 *
 *   node 02_intermediate/11_partials/lesson.js
 *
 * {% partial file="..." %} lets one Markdoc document include another.
 * Markdoc itself does no filesystem I/O, config.partials must already
 * hold every partial's parsed Ast, keyed by the exact filename used in
 * source, resolving those files from disk is your code's job. This
 * lesson includes fixtures/partials/callout.md into a small page.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Markdoc from "@markdoc/markdoc";
import { callout } from "../../fixtures/config-tags.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = path.join(__dirname, "..", "..", "fixtures");

function main() {
  // config.partials is a map: the exact string used in `file="..."`
  // attributes -> that file's already-parsed Ast. Markdoc reads this map
  // at transform time, it never touches the filesystem itself.
  const partialPath = "partials/callout.md";
  const partialSource = fs.readFileSync(path.join(FIXTURES_DIR, partialPath), "utf8");
  const partialAst = Markdoc.parse(partialSource);

  const config = {
    tags: { callout },
    partials: {
      [partialPath]: partialAst,
    },
  };

  const source = `# Getting started

Follow these steps to get set up.

{% partial file="partials/callout.md" /%}

Then run the CLI.
`;

  const ast = Markdoc.parse(source);
  const renderTree = Markdoc.transform(ast, config);
  const html = Markdoc.renderers.html(renderTree);

  console.log("Partial file resolved manually and added to config.partials:");
  console.log(`  "${partialPath}" -> parsed Ast (${partialAst.children.length} top-level node(s))`);
  console.log();
  console.log("Rendered HTML, partial content now inlined:");
  console.log(html);
  console.log();

  // Proof: without resolving the partial, Markdoc.validate() reports it
  // as missing, instead of silently skipping it.
  const errors = Markdoc.validate(ast, { tags: { callout } });
  console.log("Validating the same document with an EMPTY config.partials:");
  for (const error of errors) {
    console.log(`  ${error.error.id}: ${error.error.message}`);
  }
}

main();
