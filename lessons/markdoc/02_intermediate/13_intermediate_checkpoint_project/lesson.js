/**
 * Lesson 13: Intermediate checkpoint project.
 *
 * Read README.md in this folder first, then read this file top to bottom,
 * then run it with:
 *
 *   node 02_intermediate/13_intermediate_checkpoint_project/lesson.js
 *
 * No new API in this lesson. It combines Lessons 7-12: per-environment
 * variables, the validated `callout` tag, and a partials-based footer,
 * across a small 3-page doc set, validating and rendering each page to
 * converted/*.html and printing an errors-found-per-file summary.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Markdoc from "@markdoc/markdoc";
import { callout } from "../../fixtures/config-tags.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = path.join(__dirname, "..", "..", "fixtures");
const OUTPUT_DIR = path.join(__dirname, "converted");

const PAGES = {
  "index.md": `# Welcome

{% if $showBetaBanner %}
{% callout type="warning" %}
You're viewing the beta docs, some pages are still incomplete.
{% /callout %}
{% /if %}

This is the home page of a tiny 3-page doc set.

{% partial file="partials/footer.md" /%}
`,
  "install.md": `# Install

{% callout type="info" %}
Run the CLI once you've installed the package.
{% /callout %}

{% partial file="partials/footer.md" /%}
`,
  "broken.md": `# Broken page

{% callout type="urgent" %}
This page uses an invalid callout type on purpose, to show up in the summary.
{% /callout %}

{% partial file="partials/footer.md" /%}
`,
};

function buildConfig() {
  const footerPath = "partials/footer.md";
  const footerSource = fs.readFileSync(path.join(FIXTURES_DIR, footerPath), "utf8");
  const footerAst = Markdoc.parse(footerSource);

  return {
    tags: { callout },
    variables: { showBetaBanner: true },
    partials: { [footerPath]: footerAst },
  };
}

function main() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  const config = buildConfig();

  console.log(`Building ${Object.keys(PAGES).length} page(s):`);
  console.log();
  console.log("file          | errors | output bytes");
  console.log("--------------|--------|-------------");

  for (const [filename, source] of Object.entries(PAGES)) {
    const ast = Markdoc.parse(source);
    const errors = Markdoc.validate(ast, config).filter((e) => e.error.level === "error");
    const renderTree = Markdoc.transform(ast, config);
    const html = Markdoc.renderers.html(renderTree);

    const outputName = filename.replace(/\.md$/, ".html");
    fs.writeFileSync(path.join(OUTPUT_DIR, outputName), html);

    console.log(`${filename.padEnd(13)} | ${String(errors.length).padStart(6)} | ${String(html.length).padStart(12)}`);
    for (const error of errors) {
      console.log(`    -> ${error.error.id}: ${error.error.message}`);
    }
  }

  console.log();
  console.log(`Done. Output written to ${path.relative(process.cwd(), OUTPUT_DIR)}/`);
}

main();
