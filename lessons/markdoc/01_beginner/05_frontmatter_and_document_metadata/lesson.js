/**
 * Lesson 5: frontmatter and document metadata.
 *
 * Read README.md in this folder first, then read this file top to bottom,
 * then run it with:
 *
 *   node 01_beginner/05_frontmatter_and_document_metadata/lesson.js
 *
 * Markdoc.parse() captures a document's YAML frontmatter as a raw string
 * on ast.attributes.frontmatter, it does not parse the YAML for you.
 * This lesson parses it with js-yaml and feeds the result into
 * config.variables, so {% $frontmatter.title %} inside the document body
 * can reference it, the same mechanism Lesson 7 uses for any variable.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Markdoc from "@markdoc/markdoc";
import yaml from "js-yaml";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = path.join(__dirname, "..", "..", "fixtures");

function main() {
  const source = fs.readFileSync(path.join(FIXTURES_DIR, "article.md"), "utf8");
  const ast = Markdoc.parse(source);

  // ast.attributes.frontmatter is a raw YAML string, exactly the text
  // between the --- fences, unparsed. Markdoc deliberately doesn't parse
  // it for you, frontmatter conventions (YAML vs. TOML vs. JSON) vary
  // across tools, so Markdoc just hands you the raw text and lets you
  // choose.
  const rawFrontmatter = ast.attributes.frontmatter;
  console.log("Raw frontmatter string from ast.attributes.frontmatter:");
  console.log(JSON.stringify(rawFrontmatter));
  console.log();

  const frontmatter = yaml.load(rawFrontmatter);
  console.log("Parsed with js-yaml:");
  console.log(frontmatter);
  console.log();

  // The document body references {% $frontmatter.title %} and
  // {% $frontmatter.author %}. Those only resolve if config.variables
  // actually has a `frontmatter` key, transform() doesn't auto-wire
  // ast.attributes.frontmatter into config.variables.frontmatter, that
  // wiring is this lesson's code, not Markdoc's.
  const config = {
    variables: {
      frontmatter,
      name: "reader",
      showBanner: true,
    },
  };

  const renderTree = Markdoc.transform(ast, config);
  const html = Markdoc.renderers.html(renderTree);
  console.log("Rendered HTML, frontmatter values now resolved inline:");
  console.log(html);
}

main();
