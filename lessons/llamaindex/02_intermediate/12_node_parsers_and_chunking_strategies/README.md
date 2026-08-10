# Lesson 12: Node parsers and chunking strategies

## Splitting is a strategy, not a single fixed step

Lesson 2 used `SentenceSplitter` as if it were the only way to turn a
`Document` into `Node`s, and by default it is what `Settings` uses under
the hood whenever an `Index` builds itself. But LlamaIndex ships several
node parsers under `llama_index.core.node_parser`, each trading off
differently between simplicity, speed, and how much they respect the
source text's structure. This lesson contrasts the two simplest: the
`SentenceSplitter` you already know, and `TokenTextSplitter`, a plainer
alternative with no sentence awareness at all.

| | `SentenceSplitter` | `TokenTextSplitter` |
|---|---|---|
| Boundary awareness | Tries to end chunks on sentence boundaries | None, cuts wherever the token budget runs out |
| Config | `chunk_size` (tokens), `chunk_overlap` | `chunk_size` (tokens), `chunk_overlap`, `separator` |
| Speed/complexity | Slightly more work per chunk | Simpler, closer to a raw fixed-size cut |
| LangChain equivalent | `RecursiveCharacterTextSplitter` (tries separators in priority order) | `CharacterTextSplitter` / `TokenTextSplitter` (fixed-size, one separator) |

Both are pure local computation, same as Lesson 2, no LLM or embedding
calls involved, chunking is just string manipulation.

## Other parsers that exist but aren't covered here

`llama_index.core.node_parser` also ships `SentenceWindowNodeParser`
(splits into single sentences but attaches a window of surrounding
sentences as metadata, for retrieving a small chunk while synthesizing
with more context) and `SemanticSplitterNodeParser` (uses embedding
similarity between sentences to decide where topic boundaries fall,
rather than a fixed token count). Both are worth knowing exist; this
lesson sticks to the two parsers that need no LLM or embedding calls, to
stay cheap and to keep the comparison to boundary strategy alone.

## The code, piece by piece

```python
sentence_splitter = SentenceSplitter(chunk_size=60, chunk_overlap=10)
sentence_nodes = sentence_splitter.get_nodes_from_documents([remote_work_doc])

token_splitter = TokenTextSplitter(chunk_size=60, chunk_overlap=10)
token_nodes = token_splitter.get_nodes_from_documents([remote_work_doc])
```

Same `chunk_size`/`chunk_overlap` budget for both, on purpose, so any
difference in node count or boundaries comes from the splitting
*strategy*, not from a different size setting. `chunk_size=60` (tokens)
is deliberately small here, small enough that a ~1000-character document
actually splits into more than a dozen Nodes, making the difference in
boundaries visible.

```python
sentence_chunk_8 = sentence_nodes[8].text.strip()
token_chunk_11 = token_nodes[11].text.strip()
```

Two chunks that happen to cover the same region of the source text (the
"for tax and legal reasons." sentence), picked by inspecting both node
lists. `SentenceSplitter` stops its chunk exactly at that sentence's
period; `TokenTextSplitter`'s corresponding chunk runs straight through
the period into the start of the next sentence, because it has no notion
of "sentence" at all, only a token count and a separator (a space, by
default) to split on.

## Running it

```bash
uv run python lessons/llamaindex/02_intermediate/12_node_parsers_and_chunking_strategies/lesson.py
```

## Expected output

No LLM or embedding calls, so this is exact (character counts, node
counts, and chunk text are all deterministic for a fixed document and
fixed settings). Two informational warning lines print first, from
LlamaIndex's own metadata-length check, expected and harmless at this
small a `chunk_size`:

```
Document: remote_work_policy.txt, 1056 characters

Metadata length (37) is close to chunk size (60). Resulting chunks are less than 50 tokens. Consider increasing the chunk size or decreasing the size of your metadata to avoid this.
Metadata length (39) is close to chunk size (60). Resulting chunks are less than 50 tokens. Consider increasing the chunk size or decreasing the size of your metadata to avoid this.
SentenceSplitter (chunk_size=60, chunk_overlap=10): 14 nodes
  [0] (116 chars) 'Nimbus Robotics: Remote Work Policy  Nimbus Robotics operates on a hyb'...
  [1] (109 chars) 'a hybrid schedule: employees on the Engineering and Product teams are '...
  [2] (64 chars) 'expected in the Cluj office on Tuesday, Wednesday, and Thursday,'...
  [3] (87 chars) 'office on Tuesday, Wednesday, and Thursday, and may work remotely on M'...
  [4] (104 chars) 'Employees on fully remote contracts, agreed at hiring time, are exempt'...
  [5] (105 chars) 'Employees may work from a different country for up to 20 business days'...
  [6] (90 chars) 'as long as they remain reachable during their normal working hours in '...
  [7] (71 chars) "Longer stints require sign-off from both the employee's manager and HR"...
  [8] (26 chars) 'for tax and legal reasons.'...
  [9] (88 chars) 'Home office equipment: every employee gets a one-time 800 EUR stipend '...
  [10] (97 chars) 'chair, and monitor, reimbursed against receipts submitted within the f'...
  [11] (99 chars) 'A company laptop is provided separately and is not part of this stipen'...
  [12] (98 chars) 'when every team member is expected to be reachable regardless of which'...
  [13] (29 chars) 'are 11:00 to 16:00 Cluj time.'...

TokenTextSplitter (chunk_size=60, chunk_overlap=10): 20 nodes
  [0] (96 chars) 'Nimbus Robotics: Remote Work Policy  Nimbus Robotics operates on a hyb'...
  [1] (111 chars) 'Robotics operates on a hybrid schedule: employees on the Engineering a'...
  [2] (94 chars) 'and Product teams are expected in the Cluj office on Tuesday, Wednesda'...
  [3] (105 chars) 'Wednesday, and Thursday, and may work remotely on Monday and Friday. E'...
  [4] (91 chars) 'and Friday. Employees on fully remote contracts, agreed at hiring time'...
  [5] (97 chars) 'at hiring time, are exempt from the in-office days entirely.  Employee'...
  [6] (103 chars) 'days entirely.  Employees may work from a different country for up to '...
  [7] (97 chars) 'up to 20 business days per year without special approval, as long as t'...
  [8] (100 chars) 'approval, as long as they remain reachable during their normal working'...
  [9] (106 chars) 'their normal working hours in their home timezone. Longer stints requi'...
  [10] (97 chars) "require sign-off from both the employee's manager and HR, for tax and "...
  [11] (89 chars) 'for tax and legal reasons.  Home office equipment: every employee gets'...
  [12] (78 chars) 'every employee gets a one-time 800 EUR stipend for a desk, chair, and '...
  [13] (93 chars) 'a desk, chair, and monitor, reimbursed against receipts submitted with'...
  [14] (98 chars) 'receipts submitted within the first 60 days of employment. A company l'...
  [15] (92 chars) 'A company laptop is provided separately and is not part of this stipen'...
  [16] (93 chars) 'is not part of this stipend.  Core collaboration hours, when every tea'...
  [17] (111 chars) 'collaboration hours, when every team member is expected to be reachabl'...
  [18] (66 chars) "regardless of which days they're in the office, are 11:00 to 16:00"...
  [19] (29 chars) 'are 11:00 to 16:00 Cluj time.'...

SentenceSplitter node [8]: 'for\ntax and legal reasons.'
TokenTextSplitter node [11]: 'for\ntax and legal reasons.\n\nHome office equipment: every employee gets a one-time 800 EUR'

SentenceSplitter stopped right at the sentence-ending period; TokenTextSplitter's token budget ran out mid-way into the next sentence instead.

LangChain comparison: TokenTextSplitter here is the closer analogue of LangChain's plain CharacterTextSplitter or TokenTextSplitter (a fixed-size cut with a separator, no structural awareness), while SentenceSplitter is the closer analogue of RecursiveCharacterTextSplitter (tries several separators in priority order to avoid cutting mid-sentence, per Lesson 2's README).
```

At the same `chunk_size` budget, `TokenTextSplitter` produced more,
smaller-feeling chunks (20 vs 14) because it never gives up token budget
to land on a clean sentence boundary the way `SentenceSplitter` does.

## Checkpoint

- Node parsers are swappable strategies, not one fixed step,
  `llama_index.core.node_parser` ships several beyond the
  `SentenceSplitter` used since Lesson 2.
- **`TokenTextSplitter`**: a plainer, faster alternative with no sentence
  awareness, cuts strictly on a token budget and a separator.
- At the same `chunk_size`/`chunk_overlap`, the two parsers produce
  different node counts and different boundaries on identical text, the
  strategy matters, not just the numbers.
- `SentenceWindowNodeParser` and `SemanticSplitterNodeParser` also exist
  in this version for more advanced boundary strategies, not covered
  here to keep this lesson LLM/embedding-call-free.
- `SentenceSplitter` maps to LangChain's `RecursiveCharacterTextSplitter`;
  `TokenTextSplitter` maps to LangChain's plain `CharacterTextSplitter`
  or `TokenTextSplitter`.

If anything here still feels unclear, ask before moving to Lesson 13.
