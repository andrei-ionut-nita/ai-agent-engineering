import Markdoc from "@markdoc/markdoc";

// A single custom tag: {% callout type="info|warning|error" %}...{% /callout %}
// `render: "Callout"` is just a string label. Nothing renders it as an actual
// <div> until a renderer (HTML string template, or a React component map)
// decides what "Callout" means.
export const callout = {
  render: "Callout",
  attributes: {
    type: {
      type: String,
      default: "info",
      matches: ["info", "warning", "error"],
    },
  },
};

// A parent/child pair of custom tags: {% tabs %}{% tab title="..." %}...{% /tab %}{% /tabs %}
// `tabs` doesn't know anything about `tab`'s content ahead of time, it just
// reads its own `node.children`, already-transformed by Markdoc, and passes
// them straight through as the Tag's children.
export const tabs = {
  render: "Tabs",
  transform(node, config) {
    return new Markdoc.Tag("Tabs", {}, node.transformChildren(config));
  },
};

export const tab = {
  render: "Tab",
  attributes: {
    title: { type: String, required: true },
  },
  transform(node, config) {
    const attributes = node.transformAttributes(config);
    return new Markdoc.Tag("Tab", attributes, node.transformChildren(config));
  },
};
