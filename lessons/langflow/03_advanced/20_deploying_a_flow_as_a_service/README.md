# Lesson 20: deploying a flow as a service

## Where we left off

Every REST call so far (Lessons 7, 8, 11, 16) went to the full
`langflow run` server, the same one hosting the canvas, the Playground,
account management, everything. `lfx serve` is smaller: point it at a
`flow.json`, get back a standalone API server for exactly that flow and
nothing else, no UI, no canvas, no login.

## Why this matters

The full Langflow server is what you build and iterate on a flow with.
It's not what you'd actually want running in production for a flow
that's done, a UI server is a lot of surface area (and dependencies) to
carry just to answer `POST /run`. `lfx serve` is the deployment-shaped
version: one flow (or a folder of them), one lightweight process, the
same shape a small internal service or a Docker container running a
single flow would actually look like.

## Do this yourself

```bash
export LANGFLOW_API_KEY=<the same key from Lesson 7>
uv run lfx serve lessons/langflow/01_beginner/02_first_flow/flow.json --port 8123
```

Run this in its own terminal, leave it running. In a second terminal:

```bash
curl http://127.0.0.1:8123/flows -H "x-api-key: $LANGFLOW_API_KEY"
curl -X POST http://127.0.0.1:8123/flows/<flow_id>/run \
  -H "x-api-key: $LANGFLOW_API_KEY" -H "Content-Type: application/json" \
  -d '{"input_value": "Say hello in exactly three words."}'
```

Notice the response shape: `{"result": "...", "success": true, ...}`,
different from the full server's `outputs[].outputs[].messages[]`
nesting from Lesson 11. `lfx serve` is a separate, smaller API surface,
not a mirror of the full one.

## The code, piece by piece

```python
subprocess.Popen(
    [sys.executable, "-m", "lfx", "serve", str(FLOW_PATH), "--port", str(PORT)],
    ...
)
```

The same command as "Do this yourself," just started from Python so
`lesson.py` stays a single self-contained script, in a real deployment
you'd run the `lfx serve ...` command directly instead.

```python
for _ in range(30):
    try:
        httpx.get(f"{SERVE_URL}/flows", headers=HEADERS, timeout=1)
        return process
    except httpx.TransportError:
        time.sleep(1)
```

The server takes a moment to start up, this polls until it actually
answers instead of guessing a fixed sleep duration.

```python
response = httpx.post(f"{SERVE_URL}/flows/{flow_id}/run", ...)
print(f"Result: {response.json()['result']}")
```

Same idea as `run_flow()` from Lesson 11, `flows/{flow_id}/run` instead
of `api/v1/run/{flow_id}`, and the response's answer lives under
`result`, not nested several levels deep.

## Running it

```bash
uv run python lessons/langflow/03_advanced/20_deploying_a_flow_as_a_service/lesson.py
```

This lesson starts its own server and shuts it down when it's done, no
`langflow run` from Lesson 1 needed for this one.

## Expected output

Approximate, Gemini's exact phrasing varies:

```
Served flow: First Flow (a9aa40b1-f79a-53a4-958c-8db9b9d14082)
Result: Hello to you!
```

## Checkpoint

- **`lfx serve <flow.json>`**: a standalone API server for one flow (or
  a folder of them), no UI, no canvas, the deployment shape of a flow
  that's done being iterated on.
- **a different, smaller API surface**: `/flows` and
  `/flows/{id}/run`, not the full server's `/api/v1/...` routes, and a
  flatter response shape.
- **when to reach for this over the full server**: once a flow is
  settled and you just need something answering requests, not a place
  to keep building on the canvas.

If anything here still feels unclear, ask before moving to Lesson 21.
