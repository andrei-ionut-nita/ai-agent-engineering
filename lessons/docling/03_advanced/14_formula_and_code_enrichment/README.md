# Lesson 14: formula and code enrichment options

## Two more optional model passes

`do_formula_enrichment` and `do_code_enrichment` are both off by
default, the same as `do_ocr` and `do_table_structure` are on by
default in Lesson 7, docling only pays for a model pass you actually
ask for. When enabled, they run a dedicated model over regions the
layout model already classified as a formula or as code: formula
enrichment recovers LaTeX from a rendered equation, code enrichment
recovers the programming language and cleaner formatting from a code
block.

```python
options = PdfPipelineOptions()
options.do_formula_enrichment = True
options.do_code_enrichment = True
```

## An honest result on this course's fixture

`research_note.pdf` was built with reportlab to look roughly
formula-like and code-like, a `theta = theta - eta * gradient(...)`
line and a small Python function. Running this lesson against it, the
layout model does classify the formula-like line as a generic
`picture` region, but not specifically as `DocItemLabel.FORMULA`, and
the code line stays classified as plain `text`, not `DocItemLabel.CODE`.
That means enrichment never actually triggers on this fixture:
formula and code enrichment only run on regions the layout model
already labeled as formula or code, and a reportlab-rendered line
without real LaTeX typesetting or syntax highlighting doesn't reliably
produce that classification.

This isn't a docling limitation, it's a limitation of a synthetic
fixture generated for this course. On a real research paper PDF, with
actual LaTeX-rendered equations and syntax-highlighted code blocks
(the visual patterns these models were trained to recognize), formula
and code enrichment reliably classify and recover both. If you want to
see it work, try these options against a real arXiv PDF, docling's own
documentation examples use exactly that.

## Running it

```bash
uv run python lessons/docling/03_advanced/14_formula_and_code_enrichment/lesson.py
```

## Expected output

```
Detected items:
  section_header: Note: Batch Size and Convergence
  text: The loss update for mini-batch gradient descent follows the standard r
  picture:
  section_header: A reference implementation of the update step:
  text: def sgd_step(theta, grad, eta=0.01): return theta - eta * grad

Items classified specifically as formula or code: 0
This fixture is a reportlab-rendered PDF, not real LaTeX-typeset math or a syntax-highlighted code block, so the layout model may not classify its formula-like line as a 'formula' region the way it reliably would on a real research paper. See README.md for what this demonstrates and doesn't.
```

## Checkpoint

- **`do_formula_enrichment` / `do_code_enrichment`**: both off by
  default, each runs an extra model pass over regions already
  classified as formula or code by the layout model.
- **Enrichment depends on correct upstream classification**: these
  options do nothing for a region the layout model didn't already tag
  as `DocItemLabel.FORMULA` or `DocItemLabel.CODE`.
- **Synthetic fixtures have real limits**: a reportlab-rendered
  approximation of a formula isn't the same visual pattern as real
  LaTeX typesetting, results on real research PDFs will differ from
  what this lesson's fixture shows.

If anything here still feels unclear, ask before moving to Lesson 15.
