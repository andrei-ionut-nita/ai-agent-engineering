"""The server half of Lesson 21: a bearer-token-protected HTTP server."""

from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP

VALID_TOKEN = "secret-token-123"


class StaticTokenVerifier(TokenVerifier):
    """A minimal, hardcoded token check. A real server would look the
    token up in a database or call an identity provider here."""

    async def verify_token(self, token: str) -> AccessToken | None:
        if token != VALID_TOKEN:
            return None
        return AccessToken(token=token, client_id="demo-client", scopes=["mcp"])


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


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
