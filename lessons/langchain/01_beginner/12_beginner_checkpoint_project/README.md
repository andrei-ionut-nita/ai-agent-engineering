# Lesson 12: Beginner Checkpoint - Prompted Story Generator

## What this is

No new concepts in this lesson. This is a checkpoint: a small, real
script built entirely out of ideas from Lessons 1 through 11, combined
into one thing. If you can read `lesson.py` and understand why every
piece is there, you've mastered the Beginner tier. If any piece feels
unfamiliar, that's a sign to revisit the lesson it came from before
continuing to Intermediate.

## What it does

Generates a two-sentence, atmospheric "mystery" story opening for each
of several different characters, all in a consistent style, using one
batch call instead of a loop.

## Where each piece came from

```python
model = init_chat_model("google_genai:gemini-3.5-flash-lite", temperature=0.9)
```
Lesson 11 (provider chosen by string) and Lesson 10 (`temperature`,
along with its honest caveat: this specific model ignores it).

```python
examples = [...]
example_prompt = ChatPromptTemplate.from_messages([...])
few_shot_prompt = FewShotChatMessagePromptTemplate(examples=examples, example_prompt=example_prompt)
```
Lesson 5. Two worked examples teach the model the exact style we want
(two sentences, atmospheric, no dialogue) far more precisely than
describing it in words would.

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "... {genre} ..."),
    few_shot_prompt,
    ("human", "Character: {character_name}"),
])
```
Lesson 3 (templates) and Lesson 4 (two blanks in one template: `{genre}`
and `{character_name}`).

```python
mystery_prompt = prompt.partial(genre="mystery")
```
Lesson 4's `.partial()`. Every story in this run shares the same genre,
so it's locked in once, and only `character_name` needs to be supplied
per call from here on.

```python
def add_word_count(opening: str) -> dict:
    return {"opening": opening, "word_count": len(opening.split())}
```
Lesson 8's `RunnableLambda` pattern: our own plain function, doing
something no built-in LangChain piece does for us.

```python
chain = mystery_prompt | model | StrOutputParser() | RunnableLambda(add_word_count)
```
Lesson 6 (chaining with `|`), Lesson 7 (`StrOutputParser`, so the model's
`AIMessage` becomes plain text before our word-count function ever sees
it), and Lesson 8 again (wiring our function in as the last step).

```python
results = chain.batch([{"character_name": name} for name in characters])
```
Lesson 9. Three different characters, one `.batch()` call, run
concurrently instead of three separate `.invoke()` calls in a loop.

## Running it

```bash
uv run python lessons/langchain/01_beginner/12_beginner_checkpoint_project/lesson.py
```

You should see three different story openings, all sharing the same
atmospheric mystery style (proof the few-shot examples and system
prompt are steering things consistently), each with its own accurate
word count.

## Try this yourself

Without looking anything up:

- Change `genre="mystery"` to a different genre, and add matching new
  examples in `examples`, does the style shift accordingly?
- Add a fourth name to `characters`, does the batch handle it with no
  other changes needed?
- Swap `RunnableLambda(add_word_count)` for a different custom function
  of your own, say, one that counts sentences instead of words.

If you can make these changes confidently, you're ready for the
Intermediate tier, starting at Lesson 13.
