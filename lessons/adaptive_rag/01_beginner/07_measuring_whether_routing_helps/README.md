# Lesson 7: Measuring Whether Routing Helps

## Where we left off

Lesson 6 finished the three-route router. Every lesson since Lesson 1
has argued, in prose, that routing should do better than always running
one fixed strategy. This lesson finally checks that claim against real
answers instead of asserting it: a small labeled question set, run both
ways, routed and always-naive, scored against what each answer should
contain.

## A small labeled evaluation set

Seven questions, spanning all three labels this course classifies into:
three `simple_factual`, two `multi_hop`, two `ambiguous`. Each one
carries what a correct answer needs to contain, a phrase or a small set
of phrases:

```python
EVAL_SET = [
    {
        "question": "What oven setting does the pizza dough recipe use?",
        "type": "simple_factual",
        "expect_any_of": ["highest oven"],
    },
    ...
]
```

`is_correct()` checks, case-insensitively, whether the answer contains
the expected phrase (`expect_any_of`) or all of a small set of them
(`expect_all_of`, used for the multi-hop and ambiguous questions, where
a correct answer genuinely needs to mention facts from more than one
document). This is a simple, honest correctness check, not a proper
evaluation harness (that's a much bigger subject this series doesn't
fully build out until later intermediate and advanced lessons), but it's
enough to tell a routed answer that actually contains the right facts
from a naive answer that's missing half of them.

## Routed vs. always-naive

```python
def answer_always_naive(question: str, store: list[dict]) -> str:
    retrieved = retrieve(question, store, k=1)
    return generate_answer(question, retrieved)
```

The baseline: `naive_rag`'s exact top-1 shape, run on every question in
the set regardless of what type it is, no classification, no widening,
no grading. `answer_routed()` (Lesson 6's `answer()`, renamed here to
line up next to its baseline) is the other column: classify first, then
run whichever of the three strategies the label points to.

## Where the two should diverge

On the three `simple_factual` questions, routed and always-naive do the
same thing, `simple_factual` routes to naive top-1 anyway, so no
difference is expected there. The interesting rows are `multi_hop` and
`ambiguous`: always-naive is still stuck at k=1 on those, the exact
failure Lesson 1 demonstrated, while routed retrieves more broadly (or
grades and retries) specifically because the label told it to. If
routing is doing its job, those are the rows where routed should get
credit that always-naive doesn't.

## Running it

```bash
uv run python lessons/adaptive_rag/01_beginner/07_measuring_whether_routing_helps/lesson.py
```

## Expected output

```
type            routed   naive    question
simple_factual  True     True     What oven setting does the pizza dough recipe use?
simple_factual  True     True     How often does the wind sensor need re-oiling?
simple_factual  True     True     How often is the tomato bed watered in summer?
multi_hop       True     <often False>  What two hobbies happen in the same room as the weather station?
multi_hop       True     True/False     Where does the basil on the pizza come from?
ambiguous       True/False  False   How does wind speed affect things around the house?
ambiguous       True     False    Is wind generally something to plan around at this house?

Routed:       6-7/7 correct
Always-naive: 3-5/7 correct
```

An actual run scored routed 6/7 against always-naive 4/7. The
`simple_factual` rows should match every run, both strategies are doing
the identical thing there. The `multi_hop` and `ambiguous` rows are
where routing earns its keep and where the totals diverge: always-naive
is structurally stuck at k=1 on those, so it misses at least one of them
most runs. Routed can occasionally miss one too, this check is a plain
substring match against Gemini's actual wording (`"re-oil"`, `"dr"` for
dry/drying/dries), and a run that phrases the sensor fix as
"lubrication" instead of "re-oiling" won't match even though the answer
is correct. That's a real limitation of a keyword-contains check, not a
routing failure, and it's exactly the kind of thing a stricter
evaluation (later in this series) is built to catch. What should hold
up run to run is the *direction*: routed at or above always-naive in
total, with the gap concentrated in the `multi_hop` and `ambiguous`
rows.

## Checkpoint

- A labeled evaluation set with an explicit expected-contains check
  turns "routing should help" from a claim into something you can
  actually see pass or fail, per question.
- Routed and always-naive should tie on `simple_factual` questions,
  that's expected, not a bug, both strategies converge to the same
  thing there.
- The gap this lesson is built to expose shows up on `multi_hop` and
  `ambiguous` questions specifically, the exact two categories naive
  top-1 alone was never shaped to answer.

If anything here still feels unclear, ask before moving to Lesson 8.
