# Lesson 21: the Webhook component

## Where we left off

Every flow so far started because a person (or `lesson.py`, standing in
for one) sent an input, the Playground, `run_flow_from_json`, `POST
/api/v1/run/{id}`. A **Webhook** component starts a flow a different
way: an external system, a payment provider, a CI pipeline, a Git
host, POSTs a JSON payload to a URL, and the flow just runs, with no
one on the other end waiting for a chat-shaped answer back.

## Do this yourself

1. Add a **Webhook** component (search "webhook") and a **Chat Output**,
   wire the Webhook's output into the Chat Output.
2. Open the Webhook component's settings, copy the **Endpoint** URL and
   the pre-filled **cURL** command it shows you, that's a ready-to-run
   example of exactly how an external system would call this flow.
3. Run that cURL command yourself (or use `lesson.py`'s `trigger_webhook`,
   same request). Notice the response comes back immediately,
   `202 Accepted`, "Task started in the background," the flow hasn't
   finished yet, it's just been told to start.
4. Open **Traces** or the flow's message history in the UI a few
   seconds later, the payload you sent should show up as the flow's
   output, proof it ran, just not synchronously.

## Why this is a different shape than every earlier REST call

Lesson 11's `POST /api/v1/run/{flow_id}` waits for the flow to finish
and hands you the answer in the same response. `POST
/api/v1/webhook/{flow_id}` doesn't, it queues a background task and
returns right away. That's the point: a real webhook sender (Stripe, a
CI system, GitHub) fires an event and moves on, it doesn't sit around
waiting for your flow's model call to finish. Getting the result back
means asking again afterward, this lesson does that with
`GET /api/v1/monitor/messages`, the same endpoint the UI's message
history reads from.

## The code, piece by piece

```python
def trigger_webhook(flow_id: str, payload: dict) -> None:
    response = httpx.post(f"{LANGFLOW_URL}/api/v1/webhook/{flow_id}", headers=HEADERS, json=payload, timeout=15)
```

The whole payload just gets forwarded as-is into the Webhook
component's `data` field, whatever JSON shape an external system sends
is what `build_data()` (this component's one output method) parses.

```python
def wait_for_result(flow_id: str) -> str:
    for _ in range(15):
        time.sleep(1)
        response = httpx.get(f"{LANGFLOW_URL}/api/v1/monitor/messages", headers=HEADERS, params={"flow_id": flow_id})
```

A webhook-triggered run gets its own auto-generated `session_id` (the
`flow_id` itself, not something you can set ahead of time the way
Lesson 8 set one explicitly), so this polls by `flow_id` instead of a
known `session_id`, checking back until the background task has
actually produced a message.

## Running it

```bash
uv run python lessons/langflow/03_advanced/21_webhooks_and_external_triggers/lesson.py
```

## Expected output

Exact, this lesson's flow does no model call, it just echoes the
webhook payload back through Chat Output as proof it ran:

```
Webhook accepted: 202 {'message': 'Task started in the background', 'status': 'in progress'}
Flow's stored output:
```json
{
  "event": "order_placed",
  "order_id": 42
}
```
```

## Checkpoint

- **`POST /api/v1/webhook/{flow_id}`**: fires a flow in the background,
  `202 Accepted` immediately, no waiting for the result in the same
  response, unlike `/api/v1/run/{flow_id}`.
- **`GET /api/v1/monitor/messages?flow_id=...`**: how you check on a
  webhook-triggered run afterward, the same store the UI's own message
  history reads from.
- **when to reach for a Webhook over `/run`**: whenever the caller is
  another system firing an event, not a person or script waiting
  synchronously for an answer.

If anything here still feels unclear, ask before moving to Lesson 22,
the Advanced capstone.
