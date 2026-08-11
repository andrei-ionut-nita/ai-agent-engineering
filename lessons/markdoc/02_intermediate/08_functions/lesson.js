/**
 * Lesson 8: functions.
 *
 * Read README.md in this folder first, then read this file top to bottom,
 * then run it with:
 *
 *   node 02_intermediate/08_functions/lesson.js
 *
 * A variable gives you a value. A function lets a document compute one.
 * {% uppercase($title) %} calls a custom function registered on
 * config.functions, this lesson defines two: the uppercase() helper
 * shared via fixtures/config-functions.js (reused again in Lesson 15),
 * and a second, lesson-local one to show functions can take multiple
 * arguments.
 */

import Markdoc from "@markdoc/markdoc";
import { uppercase } from "../../fixtures/config-functions.js";

// A second function, defined locally to show a function receiving more
// than one positional argument. `parameters` is always an array, in the
// order the arguments were written in source.
const repeat = {
  transform(parameters) {
    // `parameters` isn't a real array, it's an object keyed by position
    // ("0", "1", ...), Object.values() turns it into one.
    const [text, count] = Object.values(parameters);
    return String(text).repeat(Number(count));
  },
};

function main() {
  const config = {
    functions: { uppercase, repeat },
    variables: { title: "shipping update", divider: "-" },
  };

  const source = `# {% uppercase($title) %}

{% repeat($divider, 20) %}

Functions receive already-resolved values, {% uppercase($title) %} first
resolves $title to "shipping update", then calls uppercase() with that
string, functions never see the literal text "$title".
`;

  const ast = Markdoc.parse(source);
  const renderTree = Markdoc.transform(ast, config);
  const html = Markdoc.renderers.html(renderTree);

  console.log("Config functions registered:", Object.keys(config.functions));
  console.log();
  console.log("Rendered HTML:");
  console.log(html);
}

main();
