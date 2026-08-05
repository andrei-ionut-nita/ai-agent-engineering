# Course index

A linear, one-concept-per-lesson path through the Model Context
Protocol (MCP): building MCP servers first (tools, resources, prompts),
then MCP clients, then wiring MCP tools into a real LangChain/Gemini
agent. Do these in order, top to bottom, each lesson folder has a
`README.md` (read first) and a `lesson.py` (run second). Don't move to
the next lesson until the current one's checkpoint questions feel
solid.

This course assumes you've done the [langchain](../langchain/) course,
or already know `@tool`, `bind_tools`, and the manual tool-calling loop
(Lessons 13-16 there). MCP tools are a server-hosted version of the
exact same idea: a name, a description, and an argument schema, just
served over a protocol instead of imported as a Python function.

Setup: `GOOGLE_API_KEY` in a `.env` file at the project root (get a
free key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)),
then `uv run python lessons/mcp/<NN>_<name>/lesson.py` from the project
root. Some lessons also use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector),
a Node-based dev tool: `npx @modelcontextprotocol/inspector <command>`.

## Beginner: building an MCP server, no client or LLM yet

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_mcp](01_beginner/01_what_is_mcp/) | Host/client/server, JSON-RPC, why MCP exists |
| 02 | [first_server](01_beginner/02_first_server/) | `FastMCP`, `@mcp.tool()`, `mcp.run()` |
| 03 | [tool_schemas_from_types](01_beginner/03_tool_schemas_from_types/) | How type hints and docstrings become a JSON Schema |
| 04 | [multiple_tools](01_beginner/04_multiple_tools/) | Several tools on one server |
| 05 | [resources](01_beginner/05_resources/) | `@mcp.resource()`, exposing data instead of actions |
| 06 | [prompts](01_beginner/06_prompts/) | `@mcp.prompt()`, reusable interaction templates |
| 07 | [tool_error_handling](01_beginner/07_tool_error_handling/) | A failing tool call, without crashing the server |
| 08 | [logging_on_stdio](01_beginner/08_logging_on_stdio/) | Why `print()` breaks a stdio server |
| 09 | [inspecting_with_mcp_inspector](01_beginner/09_inspecting_with_mcp_inspector/) | The MCP Inspector as your dev loop |
| 10 | [beginner_checkpoint_project](01_beginner/10_beginner_checkpoint_project/) | **Checkpoint:** Notes Server (tools + resources + prompts) |

## Intermediate: building an MCP client, then handing it to an LLM

| # | Lesson | Concept |
|---|--------|---------|
| 11 | [first_client](02_intermediate/11_first_client/) | `stdio_client`, `ClientSession`, listing tools |
| 12 | [calling_tools_from_a_client](02_intermediate/12_calling_tools_from_a_client/) | `call_tool`, reading `CallToolResult.content` |
| 13 | [reading_resources_and_prompts](02_intermediate/13_reading_resources_and_prompts/) | `read_resource`, `get_prompt` from a client |
| 14 | [content_blocks_and_structured_output](02_intermediate/14_content_blocks_and_structured_output/) | Why tool content is a list of typed blocks |
| 15 | [wiring_an_llm_to_mcp_tools](02_intermediate/15_wiring_an_llm_to_mcp_tools/) | `langchain-mcp-adapters`, `bind_tools` with Gemini |
| 16 | [multi_turn_tool_loop](02_intermediate/16_multi_turn_tool_loop/) | The full ask/call/respond loop, across turns |
| 17 | [connecting_to_multiple_servers](02_intermediate/17_connecting_to_multiple_servers/) | One agent, several MCP servers at once |
| 18 | [lifespan_and_app_context](02_intermediate/18_lifespan_and_app_context/) | Server-side startup state shared across tool calls |
| 19 | [intermediate_checkpoint_project](02_intermediate/19_intermediate_checkpoint_project/) | **Checkpoint:** Gemini Chatbot Over Two MCP Servers |

## Advanced: transports, production concerns, security

| # | Lesson | Concept |
|---|--------|---------|
| 20 | [streamable_http_transport](03_advanced/20_streamable_http_transport/) | Running a server over HTTP instead of stdio |
| 21 | [authenticating_http_servers](03_advanced/21_authenticating_http_servers/) | Bearer tokens on a remote MCP server |
| 22 | [notifications_and_list_changed](03_advanced/22_notifications_and_list_changed/) | Servers announcing that their tools changed |
| 23 | [elicitation](03_advanced/23_elicitation/) | A server asking the user a question mid-call |
| 24 | [security_and_untrusted_tool_input](03_advanced/24_security_and_untrusted_tool_input/) | Tool poisoning, confused deputies, validating arguments |
| 25 | [connecting_to_claude_desktop_and_code](03_advanced/25_connecting_to_claude_desktop_and_code/) | Wiring your server into a real MCP host |
| 26 | [advanced_capstone_project](03_advanced/26_advanced_capstone_project/) | **Capstone:** Full server + Gemini agent client, stdio and HTTP |
