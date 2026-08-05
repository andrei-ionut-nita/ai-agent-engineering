# Lesson 13: Pushing a prompt to the Prompt Hub, then pulling it back

## What we're building

A `ChatPromptTemplate`, identical in shape to the ones from the
langchain course, pushed to LangSmith's Prompt Hub under a name, then
pulled back down and used to answer a question, proving it round-trips
correctly.

## What this reveals

Every prompt so far, in this course and the last two, has lived
entirely inside a Python file. That works until a prompt needs to be
shared across scripts, edited by someone who isn't touching code, or
tracked for changes over time, then hardcoding it becomes a liability:
which file has the current version, who changed the wording last, was
this the version that scored well in Lesson 10?

The **Prompt Hub** is LangSmith's answer: a prompt stored centrally,
under a name, with every push creating a new version you can see and
roll back to from the UI. `push_prompt` stores a `ChatPromptTemplate`
object directly, `pull_prompt` fetches the current version back as the
same kind of object, ready to use in a chain exactly like one you
defined locally.

## The code, piece by piece

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer using only the given context, in one short sentence."),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])
client.push_prompt(PROMPT_NAME, object=prompt)
```

Nothing new about building the template itself (langchain course,
Lesson 3). `push_prompt` is what's new: it serializes the template and
stores it in the hub under `PROMPT_NAME`, creating a new version if the
name already exists.

```python
prompt = client.pull_prompt(PROMPT_NAME)
```

Fetches the current version back, reconstructed as a real
`ChatPromptTemplate`, not just text. From here it's used exactly like
any other prompt template, nothing downstream needs to know it came
from the hub rather than from local code.

```python
chain = prompt | model
response = chain.invoke({"context": context, "question": question})
```

Ordinary LCEL, `prompt | model`, exactly as in the langchain course.

## Running it

```bash
uv run python lessons/langsmith/02_intermediate/13_prompt_hub/lesson.py
```

In the UI, open the Prompts tab and find `langsmith-course-rag-prompt`,
with the system/human messages from above visible as its current
version.

## Checkpoint

- **Prompt Hub**: LangSmith's central, versioned store for prompts,
  separate from any one Python file.
- **`push_prompt(name, object=...)`**: stores a `ChatPromptTemplate`
  under a name, versioning each push.
- **`pull_prompt(name)`**: fetches the current version back as a usable
  `ChatPromptTemplate`.

If anything here still feels unclear, ask before moving to Lesson 14.
