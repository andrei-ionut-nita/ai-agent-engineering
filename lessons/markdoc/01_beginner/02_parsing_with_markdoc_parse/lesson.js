/**
 * Lesson 2: Markdoc.parse, the Ast, and the Tokenizer underneath it.
 *
 * Read README.md in this folder first, then read this file top to bottom,
 * then run it with:
 *
 *   node 01_beginner/02_parsing_with_markdoc_parse/lesson.js
 *
 * Markdoc.parse() is actually two steps glued together: tokenizing (source
 * string -> a flat list of tokens, borrowed from markdown-it) and building
 * (tokens -> the nested Ast tree Markdoc itself works with). This lesson
 * looks at both layers on the same short document.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Markdoc from "@markdoc/markdoc";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = path.join(__dirname, "..", "..", "fixtures");

function describeNode(node, depth = 0) {
  const indent = "  ".repeat(depth);
  const attrs = Object.keys(node.attributes).length
    ? ` attributes=${JSON.stringify(node.attributes)}`
    : "";
  console.log(`${indent}${node.type}${attrs}`);
  for (const child of node.children) {
    describeNode(child, depth + 1);
  }
}

function main() {
  const source = fs.readFileSync(path.join(FIXTURES_DIR, "hello.md"), "utf8");

  // One layer below Ast: the Tokenizer. It knows nothing about Markdoc's
  // own tags/variables syntax as *structure*, it just turns the raw string
  // into a flat token stream (headings open/close, paragraph open/close,
  // inline runs of text), the same job markdown-it's tokenizer does for
  // plain Markdown.
  const tokenizer = new Markdoc.Tokenizer();
  const tokens = tokenizer.tokenize(source);
  console.log(`Tokenizer produced ${tokens.length} tokens. First 3:`);
  for (const token of tokens.slice(0, 3)) {
    console.log(`  type=${token.type} tag=${JSON.stringify(token.tag)} content=${JSON.stringify(token.content)}`);
  }
  console.log();

  // Markdoc.parse() takes that same source, tokenizes it internally, and
  // builds the nested Ast tree on top, this is the tree the rest of the
  // pipeline (transform, validate) actually works with, not the flat
  // token list.
  const ast = Markdoc.parse(source);
  console.log(`Ast root type: ${ast.type}, ${ast.children.length} top-level child(ren)`);
  console.log();
  console.log("Ast tree (type, and attributes when present):");
  describeNode(ast);
}

main();
