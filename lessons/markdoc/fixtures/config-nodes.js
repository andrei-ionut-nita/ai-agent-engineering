import Markdoc from "@markdoc/markdoc";

const { nodes } = Markdoc;

// Overrides Markdoc's built-in `fence` node (fenced ```code``` blocks) to
// add a `data-copyable` flag and keep the language visible as a data
// attribute, on top of whatever the default fence node already does.
export const fence = {
  ...nodes.fence,
  transform(node, config) {
    const attributes = node.transformAttributes(config);
    const children = node.transformChildren(config);
    return new Markdoc.Tag(
      "pre",
      { ...attributes, "data-copyable": "true" },
      children,
    );
  },
};

// Overrides the built-in `heading` node to add an auto-generated `id`
// (a slug of the heading text), so headings become linkable anchors
// without the document author writing the id by hand.
export const heading = {
  ...nodes.heading,
  transform(node, config) {
    const attributes = node.transformAttributes(config);
    const children = node.transformChildren(config);
    const id = children
      .filter((child) => typeof child === "string")
      .join(" ")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/(^-|-$)/g, "");
    return new Markdoc.Tag(`h${node.attributes["level"]}`, { ...attributes, id }, children);
  },
};
