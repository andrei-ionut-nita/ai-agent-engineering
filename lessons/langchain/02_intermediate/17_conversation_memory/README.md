# Lesson 17: Memory is just resending the conversation

## The setup, from Lesson 14

At the end of Lesson 14 we noticed something: `messages` kept growing, one
entry at a time, and we handed the *entire* list to `.invoke()` on every
round, not just the newest message. That wasn't an accident, it was the
whole trick. This lesson makes that trick the main point.

## There is no memory inside the model

This is the single most important idea in this lesson: `ChatGoogleGenerativeAI`
does not remember anything between calls. Every `.invoke()` is a fresh,
independent request. If you called `model.invoke("My name is Nolan.")`
and then, separately, `model.invoke("What's my name?")`, the second call
has no idea the first one ever happened, because the model itself keeps
no state at all between requests.

So how does ChatGPT, or Claude, or any AI chat app "remember" what you
said five messages ago? The answer: the app keeps a growing list of every
message in the conversation, and resends the *whole list* every single
time you send a new message. The AI isn't remembering, the app is
retelling it the whole story every time, and the AI is just really good
at reading a long story and responding sensibly to the end of it.

## The code

```python
history: list[HumanMessage | AIMessage] = []
```

This list is the memory. Not the model, not some hidden setting, this
plain Python list. `HumanMessage` and `AIMessage` are the two message
types we've been using since Lesson 14, one for what the user said, one
for what the AI replied.

```python
while True:
    user_input = input("You: ").strip()
    ...
    history.append(HumanMessage(user_input))
    response = model.invoke(history)
    history.append(response)
```

Each time through the loop:

1. We read one line of input from the user.
2. We add it to `history` as a `HumanMessage`.
3. We call `model.invoke(history)`, sending the ENTIRE conversation so
   far, every message from the very beginning, not just this new one.
4. We add the model's reply to `history` too.

That fourth step matters as much as the others. If we only appended the
user's messages and never the AI's replies, the model would see its own
side of the conversation missing every time, half a conversation, and
would get confused about what it had already said.

## Why does this "feel" like memory if there isn't any?

Because from the outside, the effect is the same. By the third message,
`history` might contain: your first message, the AI's first reply, your
second message, the AI's second reply, your third message. When we call
`.invoke(history)` this time, the model reads that entire block of text
(now shaped as a list of messages instead of one string, but conceptually
the same idea) and responds the way anyone would if you handed them a
full transcript and asked "what happens next in this conversation?"

It's forgetting nothing, because it's being told everything, every
single time.

## A real limitation this creates

Every message you ever send in this loop gets resent on every future
turn. A ten-minute conversation might mean the twentieth message carries
the entire weight of the previous nineteen along with it. Two consequences:

- It costs more; you're paying (or spending free-tier quota) for the AI
  to re-read the whole history every time, not just your latest message.
- There's a limit to how much text a model can read at once (its
  **context window**). Eventually, a long enough conversation stops
  fitting, and something has to be trimmed or summarized. We're not
  solving that in this lesson, real agent frameworks handle it with
  strategies like summarizing old messages or dropping the oldest ones,
  but it's worth knowing the problem exists.

Also worth knowing: this memory lives only in the `history` Python list,
inside this one running program. Close the program, and it's gone. A
real chat app needs to save history somewhere (a database, a file) to
remember your conversation the next time you open it. We're not doing
that yet either, this lesson is deliberately the simplest version of
memory that actually works.

## Running it

```bash
uv run python lessons/langchain/02_intermediate/17_conversation_memory/lesson.py
```

Try this conversation:

```
You: My name is Nolan and my favorite color is teal.
AI:  ...

You: What is my name and favorite color?
AI:  Your name is Nolan and your favorite color is teal.
```

Then try quitting and running it again, fresh. Ask "what's my name?"
immediately. It won't know, because `history` was reset to an empty list
when the program restarted. That's proof the memory really does live in
that list, and nowhere else.

## Checkpoint

- **the model has no memory**: every `.invoke()` call is independent and
  stateless on its own.
- **conversation history**: a growing list of every message sent and
  received, resent in full on every new call, which is what creates the
  illusion of memory.
- **context window**: the limit on how much conversation a model can read
  at once; long conversations eventually exceed it.
- **in-memory only**: our `history` list disappears when the program
  ends, real persistence needs to be saved somewhere external.

If anything here still feels unclear, ask before moving to Lesson 18.
Later, Lesson 23 will show a proper agent framework managing this list
for us automatically.
