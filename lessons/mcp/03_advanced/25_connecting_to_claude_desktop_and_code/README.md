# Lesson 25: Wiring your server into a real host

## From "a client you wrote" to "a real host"

Every client in this course, from Lesson 11's `first_client` through
the checkpoint chatbot, was code you wrote yourself. A real MCP host,
Claude Desktop or Claude Code, is a client you didn't write, configured
declaratively instead of launched from a script. This lesson takes a
server from earlier in the course and wires it into one.

## The config file shape

Both Claude Desktop and Claude Code read a JSON config listing servers
under an `mcpServers` key:

```json
{
  "mcpServers": {
    "notes": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/ai_learning",
        "run",
        "python",
        "lessons/mcp/01_beginner/10_beginner_checkpoint_project/server.py"
      ]
    }
  }
}
```

This is exactly a `StdioServerParameters` in JSON form: `command` and
`args` describe the same subprocess launch every `lesson.py` in this
course has done directly. The host reads this config, launches the
server the same way `stdio_client` did, and creates one MCP client
internally to manage the connection, same three-layer picture from
Lesson 1.

**Claude Desktop**: edit
`~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) or `%AppData%\Claude\claude_desktop_config.json` (Windows),
restart the app.

**Claude Code**: run `claude mcp add` from a terminal, or edit the
project's `.mcp.json` directly with the same `mcpServers` shape.

## Why `--directory` and absolute paths matter

A host launches your server from wherever *it* runs, not from your
project folder, so a relative path like `lessons/mcp/.../server.py`
would resolve against the wrong directory. `uv --directory <path> run python <script>`
tells `uv` to change into your project directory first, so the
server's own imports and any relative paths inside it still work the
same way they do when you run it with `uv run` yourself.

## Verifying the wiring without a full host

`lesson.py` doesn't launch Claude Desktop, there's no way to script
that. Instead, it validates the exact config you'd put in
`claude_desktop_config.json`: it reads the `command`/`args` pair,
launches the subprocess exactly the way a host would, and confirms the
server responds correctly, catching the most common mistake (a wrong
path, a missing `--directory`) before you go edit a real host's config
file.

## Running it

```bash
uv run python lessons/mcp/03_advanced/25_connecting_to_claude_desktop_and_code/lesson.py
```

## Checkpoint

- **`mcpServers` config**: `command` + `args`, precisely the JSON form
  of a `StdioServerParameters` your own clients have built directly
  all course.
- **Claude Desktop**: `claude_desktop_config.json`, restart after
  editing.
- **Claude Code**: `claude mcp add`, or edit `.mcp.json` directly.
- Absolute paths and `--directory` matter because the host launches
  your server from its own working directory, not yours.

If anything here still feels unclear, ask before moving to Lesson 26,
the advanced capstone.
