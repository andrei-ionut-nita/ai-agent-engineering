/**
 * Lesson 6: Beginner checkpoint project.
 *
 * Read README.md in this folder first, then read this file top to bottom,
 * then run it with:
 *
 *   node 01_beginner/06_beginner_checkpoint_project/lesson.js
 *
 * No new API in this lesson. It combines everything from Lessons 1-5:
 * walk every top-level .md file in fixtures/, run each through the full
 * parse -> transform -> render pipeline (resolving frontmatter into
 * variables along the way), write the result to converted/*.html, and
 * print a small summary table.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Markdoc from "@markdoc/markdoc";
import yaml from "js-yaml";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = path.join(__dirname, "..", "..", "fixtures");
const OUTPUT_DIR = path.join(__dirname, "converted");

function countNodes(node) {
  return 1 + node.children.reduce((sum, child) => sum + countNodes(child), 0);
}

function convertFile(filename) {
  const source = fs.readFileSync(path.join(FIXTURES_DIR, filename), "utf8");
  const ast = Markdoc.parse(source);

  const frontmatter = ast.attributes.frontmatter
    ? yaml.load(ast.attributes.frontmatter)
    : {};

  const config = {
    variables: { frontmatter, name: "reader", showBanner: true },
  };

  const renderTree = Markdoc.transform(ast, config);
  const html = Markdoc.renderers.html(renderTree);

  return { nodeCount: countNodes(ast), html };
}

function main() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  // Only the top-level .md fixtures, not fixtures/partials/, those are
  // meant to be included by other documents, not converted standalone
  // (Lesson 11 covers partials).
  const mdFiles = fs
    .readdirSync(FIXTURES_DIR, { withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
    .map((entry) => entry.name)
    .sort();

  console.log(`Converting ${mdFiles.length} file(s) from fixtures/ to converted/:`);
  console.log();
  console.log("file           | ast nodes | output bytes");
  console.log("---------------|-----------|-------------");

  for (const filename of mdFiles) {
    const { nodeCount, html } = convertFile(filename);
    const outputName = filename.replace(/\.md$/, ".html");
    fs.writeFileSync(path.join(OUTPUT_DIR, outputName), html);
    console.log(
      `${filename.padEnd(14)} | ${String(nodeCount).padStart(9)} | ${String(html.length).padStart(12)}`,
    );
  }

  console.log();
  console.log(`Done. Output written to ${path.relative(process.cwd(), OUTPUT_DIR)}/`);
}

main();
