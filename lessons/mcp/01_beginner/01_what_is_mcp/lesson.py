"""
Lesson 1: what is MCP, no server or client yet.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/mcp/01_beginner/01_what_is_mcp/lesson.py

There's no MCP SDK usage yet. This just lays out the vocabulary the rest
of the course builds on: host, client, server, and the three things a
server can expose.
"""

PARTICIPANTS = {
    "Host": "The AI application. Claude Desktop, Claude Code, or a "
    "chatbot you build yourself in Lesson 15.",
    "Client": "One per server, created by the host, holds the "
    "connection open and speaks the protocol.",
    "Server": "The program exposing tools, resources, and prompts. "
    "What you build starting in Lesson 2.",
}

PRIMITIVES = {
    "Tools": "Functions the AI can call to DO something. "
    "Discovered with tools/list, invoked with tools/call.",
    "Resources": "Data the AI can READ for context, no action taken. "
    "Discovered with resources/list, fetched with resources/read.",
    "Prompts": "Reusable interaction templates. "
    "Discovered with prompts/list, filled in with prompts/get.",
}


def main() -> None:
    print("MCP participants:")
    for name, description in PARTICIPANTS.items():
        print(f"  {name}: {description}")

    print("\nMCP server primitives:")
    for name, description in PRIMITIVES.items():
        print(f"  {name}: {description}")

    print(
        "\nTransport: stdio (local subprocess, Lessons 2-19) or "
        "Streamable HTTP (remote server, Lessons 20+). Same protocol "
        "either way, just a different pipe underneath."
    )


if __name__ == "__main__":
    main()
