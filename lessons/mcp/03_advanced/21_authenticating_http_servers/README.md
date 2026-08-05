# Lesson 21: Bearer tokens on an HTTP server

## Why stdio never needed this

A stdio server (every lesson through 19) is launched directly by
whoever's talking to it, there's no network in between, so there's
nothing to authenticate. An HTTP server (Lesson 20) is different: it's
sitting on a port, and anything that can reach that port can send it
requests. `add` is a harmless demo, but a real server exposing, say,
database access absolutely needs to know who's asking.

## Verifying a bearer token

The SDK's building block is `TokenVerifier`, a small protocol with one
method:

```python
from mcp.server.auth.provider import AccessToken, TokenVerifier

VALID_TOKEN = "secret-token-123"


class StaticTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        if token != VALID_TOKEN:
            return None
        return AccessToken(token=token, client_id="demo-client", scopes=["mcp"])
```

Returning `None` means "reject this token", returning an `AccessToken`
means "accept it, and here's what it's allowed to do" (`scopes`). A
real server would check the token against a database or call out to an
identity provider here, this lesson hardcodes one valid token to keep
the demo self-contained.

## Wiring it into the server

```python
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "auth-demo-server",
    port=8932,
    stateless_http=True,
    token_verifier=StaticTokenVerifier(),
    auth=AuthSettings(
        issuer_url="http://127.0.0.1:8932",
        resource_server_url="http://127.0.0.1:8932",
        required_scopes=["mcp"],
    ),
)
```

`AuthSettings` describes this server as an OAuth *resource server*,
`issuer_url` and `resource_server_url` are metadata a real deployment
would point at an actual identity provider; here they just point back
at the demo server itself. The official docs note MCP recommends OAuth
for production HTTP servers precisely so a server doesn't need to
invent its own token format, this lesson's `StaticTokenVerifier` is a
minimal stand-in to demonstrate the mechanism, not a production auth
scheme.

## Sending the token from a client

```python
async with streamablehttp_client(
    "http://127.0.0.1:8932/mcp",
    headers={"Authorization": "Bearer secret-token-123"},
) as (read, write, _):
    ...
```

`streamablehttp_client` takes a plain `headers` dict, same as any HTTP
client. Omit the header, or send the wrong token, and the connection
fails with a `401 Unauthorized` before `initialize()` ever completes.

## Running it

```bash
uv run python lessons/mcp/03_advanced/21_authenticating_http_servers/lesson.py
```

You'll see three attempts: no token, the wrong token, and the correct
one, only the last one succeeds.

## Checkpoint

- **`TokenVerifier`**: one method, `verify_token`, return `None` to
  reject, an `AccessToken` to accept.
- **`AuthSettings`**: describes the server as an OAuth resource server,
  required alongside a `token_verifier`.
- A client sends its token as a normal `Authorization: Bearer ...`
  header via `streamablehttp_client(url, headers=...)`.
- This restriction is specific to network transports, stdio has no
  equivalent because there's no network boundary to guard.

If anything here still feels unclear, ask before moving to Lesson 22,
notifications.
