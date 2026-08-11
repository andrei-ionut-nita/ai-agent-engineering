# Lesson 2: `Markdoc.parse`, the `Ast`, and the `Tokenizer`

## The problem: before you can transform anything, you need a tree

Lesson 1 treated `Markdoc.parse()` as a black box, string in, `Ast` out.
This lesson opens that box: parsing is actually two layers, a flat
**token stream** underneath, and a nested **Ast** tree built on top of it.
Understanding both matters once you start writing custom tags and node
overrides later in this course, because a tag's `transform` function
receives Ast nodes, not tokens.

## Tokenizer: the flat layer

`Markdoc.Tokenizer` (borrowed from `markdown-it`'s tokenizer) turns a
source string into a flat list of open/close/inline tokens, it doesn't
know about nesting, a `heading_open` token and its matching
`heading_close` token are just two entries in a flat array, the nesting
is implied by their order, not by actual tree structure.

## Ast: the nested layer `Markdoc.parse` builds for you

`Markdoc.parse(source)` runs the tokenizer internally, then builds an
actual tree on top: a `heading` Ast node with a `text` node as its
descendant, instead of two separate open/close tokens. This is the shape
every later stage (`transform`, `validate`) actually consumes, `Ast`
nodes have `.type`, `.attributes`, and `.children`, and can be walked
recursively, which is exactly what this lesson's `describeNode()` does.

## The code, piece by piece

```javascript
const tokenizer = new Markdoc.Tokenizer();
const tokens = tokenizer.tokenize(source);
```

Calling the tokenizer directly is not something you'd normally do in real
Markdoc usage, `Markdoc.parse()` already does this internally, it's shown
here purely so the flat token layer is visible at least once.

```javascript
const ast = Markdoc.parse(source);
```

This is the call every other lesson in this course actually uses. It
tokenizes internally and returns the nested `Ast`.

```javascript
function describeNode(node, depth = 0) {
  console.log(`${indent}${node.type}...`);
  for (const child of node.children) {
    describeNode(child, depth + 1);
  }
}
```

A plain recursive walk. `node.attributes` carries per-node data:
`level` on a `heading` node, `content` on a `text` node, `marker` on a
`strong` node (which literal characters, `**` vs `__`, made it bold).

## Running it

```bash
node 01_beginner/02_parsing_with_markdoc_parse/lesson.js
```

## Expected output

```
Tokenizer produced 26 tokens. First 3:
  type=heading_open tag="h1" content=""
  type=inline tag="" content="Hello, Markdoc"
  type=heading_close tag="h1" content=""

Ast root type: document, 4 top-level child(ren)

Ast tree (type, and attributes when present):
document
  heading attributes={"level":1}
    inline
      text attributes={"content":"Hello, Markdoc"}
  paragraph
    inline
      text attributes={"content":"This is a short document used across the early lessons in this course."}
  paragraph
    inline
      text attributes={"content":"It has a "}
      strong attributes={"marker":"**"}
        text attributes={"content":"heading"}
      text attributes={"content":", a paragraph, and a list:"}
  list attributes={"ordered":false,"marker":"-"}
    item
      inline
        text attributes={"content":"First item"}
    item
      inline
        text attributes={"content":"Second item"}
    item
      inline
        text attributes={"content":"Third item"}
```

## Checkpoint

- **`Markdoc.Tokenizer`**: the flat, low-level layer, a list of
  open/close/inline tokens with implied (not actual) nesting. You'll
  rarely call this directly, `Markdoc.parse()` already does.
- **`Markdoc.parse(source)`**: builds the nested `Ast` tree on top of the
  tokenizer's output. This is what every later stage works with.
- **`Ast` node shape**: `.type`, `.attributes`, `.children`, walkable
  recursively, no config needed to produce it, parsing doesn't resolve
  tags or variables, that's transform's job (Lesson 3).

If anything here still feels unclear, ask before moving to Lesson 3.
