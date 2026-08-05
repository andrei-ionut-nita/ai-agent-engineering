# Lesson 26: Conversation summarization, compressing instead of dropping

## Where we left off

Lesson 25's `trim_messages` kept a conversation under the context window
by dropping the oldest messages entirely. That works, but it means real
information is genuinely, permanently lost, the model has no way to
recall a detail from a message that's simply gone. This lesson takes a
different approach: **compress** old messages into a short summary
instead of discarding them.

## Summarizing is just another model call

```python
def summarize(messages: list) -> str:
    transcript = "\n".join(f"{m.type}: {m.text}" for m in messages)
    summary_request = [
        HumanMessage(
            "Summarize the key facts from this conversation in one short "
            f"paragraph, keep every specific detail:\n\n{transcript}"
        )
    ]
    return model.invoke(summary_request).text
```

There's no special "summarization API", this is just a normal
`.invoke()` call, same as every one since Lesson 1, asking the model to
do a specific job: read a chunk of old conversation and compress it into
a short paragraph, being told explicitly to keep every specific detail
(names, preferences, facts), not just the general gist.

## Replacing old messages with the summary

```python
compressed_history = [
    SystemMessage(f"Summary of earlier conversation: {summary_text}")
] + recent_messages
```

Instead of keeping six original messages about a dog's name, a
favorite food, and learning violin, we keep **one** `SystemMessage`
containing their summary, plus the genuinely recent messages,
unchanged. The conversation is now much shorter overall, but the
information from the old part isn't gone, it's compressed, not deleted.

## Proof the information survived

```python
old_question = compressed_history + [HumanMessage("What is my dog's name?")]
old_answer = model.invoke(old_question)
```

Ask about the dog's name, mentioned only in the *summarized* part of the
conversation, and the model answers correctly: "Your dog's name is
Baxter!" Compare this directly to Lesson 25, where the exact same kind
of question, about information from the trimmed-away part of that
conversation, got an honest "I don't know." Same underlying problem
(a long conversation, more messages than we want to keep in full),
two different strategies, two very different outcomes for old
information.

## The real tradeoff, this time

Summarization isn't free either. It costs an extra model call every
time you summarize (the `summarize()` call itself), and a summary is, by
definition, a compressed, lossy version of the original, subtle details
or exact phrasing can still get smoothed over or lost in the compression
itself, even if the main facts survive.

Trimming is cheaper and keeps exact wording for whatever survives;
summarization costs more but preserves the gist of everything, even the
parts that no longer fit in full. Real applications often use both
together: summarize distant history, but keep the last several turns
trimmed-but-uncompressed for precision.

## Running it

```bash
uv run python lessons/langchain/03_advanced/26_conversation_summarization/lesson.py
```

## Checkpoint

- **summarization**: compressing old messages into a shorter form
  instead of dropping them, via a normal model call asked to do that
  specific job.
- **information is preserved, not deleted**: a well-written summary lets
  the model recall old facts, unlike trimming.
- **the tradeoff**: costs an extra model call, and a summary can still
  lose precision even as it preserves the main facts.

If anything here still feels unclear, ask before moving to Lesson 27.
