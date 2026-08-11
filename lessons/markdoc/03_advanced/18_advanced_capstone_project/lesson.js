/**
 * Lesson 18: Advanced capstone project.
 *
 * Read README.md in this folder first, then read this file top to bottom,
 * then run it with:
 *
 *   node 03_advanced/18_advanced_capstone_project/lesson.js
 *
 * No new API in this lesson. It's the full content pipeline this course
 * has been building toward: a folder of Markdoc source pages, each with
 * frontmatter, validated and rejected loudly on error, transformed with
 * the full composed config from Lesson 15 (custom tags, node overrides,
 * functions, partials), rendered to converted/*.html, plus a generated
 * converted/index.html linking every page that passed validation.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Markdoc from "@markdoc/markdoc";
import yaml from "js-yaml";
import { callout, tabs, tab } from "../../fixtures/config-tags.js";
import { fence, heading } from "../../fixtures/config-nodes.js";
import { uppercase } from "../../fixtures/config-functions.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = path.join(__dirname, "..", "..", "fixtures");
const OUTPUT_DIR = path.join(__dirname, "converted");

const PAGES = {
  "index.md": `---
title: Markdoc Course Site
---
# {% uppercase($frontmatter.title) %}

{% partial file="partials/footer.md" /%}
`,
  "install.md": `---
title: Installation
---
# {% $frontmatter.title %}

{% tabs %}
{% tab title="npm" %}
\`\`\`bash
npm install @markdoc/markdoc
\`\`\`
{% /tab %}
{% tab title="yarn" %}
\`\`\`bash
yarn add @markdoc/markdoc
\`\`\`
{% /tab %}
{% /tabs %}

{% partial file="partials/footer.md" /%}
`,
  "usage.md": `---
title: Usage
---
# {% $frontmatter.title %}

{% callout type="info" %}
See the earlier lessons in this course for the full pipeline this page runs through.
{% /callout %}

{% partial file="partials/footer.md" /%}
`,
  "broken.md": `---
title: Broken Page
---
# {% $frontmatter.title %}

{% callout type="not-a-real-type" %}
This page is intentionally invalid, it should be rejected, not published.
{% /callout %}

{% partial file="partials/footer.md" /%}
`,
};

function buildConfig() {
  const footerPath = "partials/footer.md";
  const footerAst = Markdoc.parse(fs.readFileSync(path.join(FIXTURES_DIR, footerPath), "utf8"));

  return {
    tags: { callout, tabs, tab },
    nodes: { fence, heading },
    functions: { uppercase },
    partials: { [footerPath]: footerAst },
  };
}

function main() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  const baseConfig = buildConfig();

  const published = [];
  const rejected = [];

  console.log(`Building ${Object.keys(PAGES).length} page(s):`);
  console.log();

  for (const [filename, source] of Object.entries(PAGES)) {
    const ast = Markdoc.parse(source);
    const frontmatter = ast.attributes.frontmatter ? yaml.load(ast.attributes.frontmatter) : {};
    const config = { ...baseConfig, variables: { frontmatter } };

    const errors = Markdoc.validate(ast, config).filter((e) => e.error.level === "error");
    if (errors.length > 0) {
      console.log(`FAIL  ${filename}: ${errors.length} validation error(s), not published`);
      for (const error of errors) {
        console.log(`        ${error.error.id}: ${error.error.message}`);
      }
      rejected.push(filename);
      continue;
    }

    const renderTree = Markdoc.transform(ast, config);
    const html = Markdoc.renderers.html(renderTree);
    const outputName = filename.replace(/\.md$/, ".html");
    fs.writeFileSync(path.join(OUTPUT_DIR, outputName), html);
    console.log(`OK    ${filename} -> ${outputName} (title: "${frontmatter.title}")`);
    published.push({ outputName, title: frontmatter.title });
  }

  // A generated index.html linking every page that passed validation,
  // built by hand (it's site scaffolding, not itself a Markdoc document).
  const indexLinks = published
    .filter((page) => page.outputName !== "index.html")
    .map((page) => `<li><a href="${page.outputName}">${page.title}</a></li>`)
    .join("");
  const indexHtml = `<article><h1>Site index</h1><ul>${indexLinks}</ul></article>`;
  fs.writeFileSync(path.join(OUTPUT_DIR, "index.html"), indexHtml);

  console.log();
  console.log(`Published: ${published.length}, rejected: ${rejected.length}`);
  console.log(`Output written to ${path.relative(process.cwd(), OUTPUT_DIR)}/, including a generated index.html`);
}

main();
