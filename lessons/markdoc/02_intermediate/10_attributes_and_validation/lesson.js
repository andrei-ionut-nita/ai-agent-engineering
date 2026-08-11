/**
 * Lesson 10: attributes and validation.
 *
 * Read README.md in this folder first, then read this file top to bottom,
 * then run it with:
 *
 *   node 02_intermediate/10_attributes_and_validation/lesson.js
 *
 * A tag's `attributes` schema (Lesson 9 briefly used `default` and
 * `matches`) isn't just documentation, Markdoc.validate() actively
 * checks it and returns structured errors, without rendering anything.
 * This lesson runs validate() on a correct document and a broken one,
 * side by side, the kind of check you'd run in CI before deploying docs.
 */

import Markdoc from "@markdoc/markdoc";
import { callout } from "../../fixtures/config-tags.js";

function main() {
  const config = { tags: { callout } };

  const validSource = `{% callout type="warning" %}\nDouble-check your API key.\n{% /callout %}\n`;
  const invalidSource = `{% callout type="urgent" %}\nThis type isn't in the schema's allowed list.\n{% /callout %}\n`;

  console.log("Validating a correct document:");
  const validAst = Markdoc.parse(validSource);
  const validErrors = Markdoc.validate(validAst, config);
  console.log(`  errors found: ${validErrors.length}`);
  console.log();

  console.log("Validating a broken document (type=\"urgent\", not in the schema's `matches` list):");
  const invalidAst = Markdoc.parse(invalidSource);
  const invalidErrors = Markdoc.validate(invalidAst, config);
  console.log(`  errors found: ${invalidErrors.length}`);
  for (const error of invalidErrors) {
    console.log(`    id: ${error.error.id}`);
    console.log(`    level: ${error.error.level}`);
    console.log(`    message: ${error.error.message}`);
  }
  console.log();

  console.log(
    "Validation is a separate step from rendering, transform() would " +
      "still happily render the invalid document (it just keeps the " +
      "attribute value as-is), validate() is what catches the mistake " +
      "before anything ships.",
  );
}

main();
