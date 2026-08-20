# Lesson 11: the REST API on its own terms

## Where we left off

Beginner reached for the REST API twice already, Lesson 7 to resolve a
Global Variable, Lesson 8 to demonstrate memory, both times as a
necessary workaround for something `run_flow_from_json` genuinely
can't do. This lesson covers the REST API properly: what else it can
do, and the auth header underneath every call you've already made.

## Do this yourself

1. Open **My Flows** in the sidebar, this is the same list `GET
   /api/v1/flows/` returns, just rendered as cards instead of JSON.
2. Open your browser's dev tools (Network tab), click into any flow,
   run it once in the Playground. Find the `POST /api/v1/run/{id}` call
   in the network log, this is the exact request `run_flow()` in
   `lesson.py` makes, just issued by the browser instead of `httpx`.
3. Notice the request has no visible `x-api-key` header, the browser
   session authenticates a different way (a cookie from your login).
   `lesson.py`'s calls aren't a browser session, so they authenticate
   with the `LANGFLOW_API_KEY` header explicitly, that's the difference
   this lesson is about.

## The code, piece by piece

```python
HEADERS = {"x-api-key": os.environ["LANGFLOW_API_KEY"]}
```

Every call in this lesson sends this same header. Drop it, and the
server rejects the request before it even looks at which flow you're
asking for, `lesson.py`'s first call does exactly this on purpose to
show the rejection.

```python
def list_flows() -> list[dict]:
    response = httpx.get(f"{LANGFLOW_URL}/api/v1/flows/", headers=HEADERS)
```

`GET /api/v1/flows/`, every flow currently stored on the server,
`upload_flow()`'s `POST /api/v1/flows/upload/` from Lesson 7 is how a
flow gets added to this list in the first place.

```python
def delete_flow(flow_id: str) -> None:
    response = httpx.delete(f"{LANGFLOW_URL}/api/v1/flows/{flow_id}", headers=HEADERS)
```

`DELETE /api/v1/flows/{flow_id}`, the opposite of upload, removes it
from the server entirely. This lesson cleans up after itself, uploading
a flow just to run and delete it, so repeated runs of `lesson.py` don't
leave a pile of identical test flows behind on your server.

## Running it

```bash
uv run python lessons/langflow/02_intermediate/11_rest_api_and_auth/lesson.py
```

## Expected output

The flow counts will differ based on what's already on your server, but
the shape should match, one fewer flow after delete than right after
upload:

```
No x-api-key header: HTTP 403
Uploaded, flow_id: 144f8776-7b97-4cb9-9ead-bb0fef4c4b81
Flows on the server: 12
Gemini said: Hello to you!
Flows after delete: 11
```

## Checkpoint

- **`x-api-key` header**: what every REST call in this course
  authenticates with, generated once via `uv run langflow api-key`
  (Lesson 7), missing it gets you a 403 before the server even looks at
  the request body.
- **`GET /api/v1/flows/`** / **`DELETE /api/v1/flows/{id}`**: list and
  remove flows on the server, the other half of the upload/run pair
  from Lesson 7.
- **the browser vs. `httpx`**: the Playground authenticates with a
  login cookie, `lesson.py` isn't a browser session so it authenticates
  with the API key header instead, same server, same endpoints, two
  different ways in.

If anything here still feels unclear, ask before moving to Lesson 12.
