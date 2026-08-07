# Lesson 11: `PUBLISH`/`SUBSCRIBE`, streaming an agent's progress

## Where we left off

Everything so far has been request/response: write a value, later read
it back. An agent working through a multi-step task (searching,
reading a document, drafting an answer) has a different need: telling
a listener what it's doing *as it happens*, not only handing back a
final result.

## Channels: no keys, no storage

```python
pubsub = r.pubsub()
pubsub.subscribe("agent:progress")
```

Pub/sub is a different mechanism from everything else in this course:
a **channel** isn't a key, nothing is stored, there's no `GET` for a
channel. A subscriber only receives messages published *while it's
subscribed*; a message published before a subscriber connects, or
after it disconnects, is simply gone, unreceived. This is intentional:
pub/sub is for live events, not a durable log (Lesson 19's streams are
the durable version of this same idea).

## Publishing

```python
r.publish("agent:progress", "searching for relevant documents...")
```

`PUBLISH channel message` sends `message` to every current subscriber
of `channel`, and returns how many subscribers received it, `0` if
nobody was listening, which still succeeds, the message isn't queued
for later, it's just not delivered to anyone.

## Listening

```python
for item in pubsub.listen():
    if item["type"] == "message":
        print(item["data"])
```

`pubsub.listen()` is a blocking generator, it yields dictionaries as
messages arrive, including a `subscribe` confirmation first, then one
`message` dict per published message, forever, until the loop is
broken or the connection closes. This lesson's script runs the
publisher and subscriber as two different execution paths within one
process (a background thread) so it can print both sides in order; a
real system typically runs them as two entirely separate processes.

## Running it

```bash
docker compose up -d redis
uv run python lessons/redis/02_intermediate/11_pub_sub_for_streaming_events/lesson.py
```

## Expected output

```
Subscribed to agent:progress
Received: searching for relevant documents...
Received: found 3 candidates, reading the top one...
Received: drafting an answer...
Received: done
```

## Checkpoint

- **channels**: not keys, nothing is stored, a message only reaches
  subscribers who are already listening when it's published.
- **`PUBLISH`**: sends a message to every current subscriber, returns
  the subscriber count, `0` if nobody's listening.
- **`pubsub.listen()`**: a blocking generator yielding each message as
  it arrives, the live-events counterpart to Lesson 19's durable
  streams.

If anything here still feels unclear, ask before moving to Lesson 12.
