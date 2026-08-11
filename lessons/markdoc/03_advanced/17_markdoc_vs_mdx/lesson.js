/**
 * Lesson 17: Markdoc vs. MDX.
 *
 * Read README.md in this folder first, then read this file top to bottom,
 * then run it with:
 *
 *   node 03_advanced/17_markdoc_vs_mdx/lesson.js
 *
 * MDX (mdxjs.com) is the other popular way to add components to
 * Markdown: it compiles Markdown + literal embedded JSX into a React
 * component, arbitrary expressions and all. This course deliberately
 * doesn't install an MDX compiler as a dependency (mixing an
 * untrusted-input-shaped tool into a learning repo isn't worth it just
 * for a comparison lesson), instead this lesson runs a concrete
 * Markdoc.validate() check that MDX has no equivalent for, and prints
 * the rest of the comparison as a table.
 */

import Markdoc from "@markdoc/markdoc";
import { callout } from "../../fixtures/config-tags.js";

const COMPARISON = {
  "Output shape": ["Data: a plain render tree (Tag objects + strings)", "Code: a compiled React component, arbitrary JS included"],
  "Untrusted authors": ["Safe by default, tags are schema-checked, no arbitrary JS execution", "Risky, embedded JSX/expressions run as real code at build/render time"],
  "Validation before render": ["Yes, Markdoc.validate() checks attributes/structure with zero execution", "No built-in equivalent, invalid JSX is a compile error, not a content error"],
  "Multiple output targets": ["Yes, same render tree to HTML (Lesson 4) or React (Lesson 16)", "No, MDX compiles straight to one target (usually a React/JS component)"],
  "Learning curve": ["A small tag/attribute syntax on top of Markdown", "Markdown syntax plus real JSX/JS knowledge to author pages"],
};

function main() {
  // Something Markdoc's validation catches structurally, an attribute
  // value outside the tag's declared schema, with zero code execution
  // involved, just a data check.
  const untrustedInput = `{% callout type="<script>alert(1)</script>" %}\nSubmitted by an untrusted author.\n{% /callout %}\n`;
  const config = { tags: { callout } };
  const ast = Markdoc.parse(untrustedInput);
  const errors = Markdoc.validate(ast, config);

  console.log("An untrusted-author-shaped input, validated with Markdoc's schema:");
  console.log(`  input:  ${JSON.stringify(untrustedInput.split("\n")[0])}`);
  console.log(`  errors: ${errors.length}`);
  for (const error of errors) {
    console.log(`    ${error.error.id}: ${error.error.message}`);
  }
  console.log(
    "  -> rejected as bad DATA (an attribute value outside the schema's " +
      "`matches` list), nothing was ever executed to reach that verdict.",
  );
  console.log();
  console.log(
    "MDX has no equivalent check: an author could write a literal " +
      "<script> tag, or arbitrary {jsExpression()} directly in an .mdx " +
      "file, and it becomes real, executable output at build time, " +
      "there's no schema step to catch it first.",
  );
  console.log();

  console.log("Markdoc vs. MDX:");
  console.log();
  const col1 = "Markdoc";
  const col2 = "MDX";
  console.log(`  ${"aspect".padEnd(24)} | ${col1.padEnd(55)} | ${col2}`);
  for (const [aspect, [markdocSide, mdxSide]] of Object.entries(COMPARISON)) {
    console.log(`  ${aspect.padEnd(24)} | ${markdocSide.padEnd(55)} | ${mdxSide}`);
  }
}

main();
