# Course index

A short, focused path through [Langflow](https://www.langflow.org/), the
visual, low-code layer for building LLM flows, using Google's Gemini free
tier (`gemini-3.5-flash-lite`). Langflow's components are, underneath,
close relatives of what the [langchain](../langchain/) and
[langgraph](../langgraph/) courses already teach: this course doesn't
re-teach nodes and edges, it teaches what a visual builder buys you over
raw code, and how to graduate a prototype built by dragging boxes into
something a team can actually maintain. Doing `langchain` first (or
already knowing `.invoke()`, prompts, and tools) will make the model/
prompt lessons feel familiar rather than new.

Every lesson has three files: a `README.md` to read first, a `lesson.py`
to run second, and (for most lessons with a visual component) a
`flow.json`. `README.md` gives you numbered actions to perform in your
own browser before you read the code, the same lesson isn't fully done
until you've done both.

One caveat worth knowing upfront: a couple of `flow.json` files in this
course are shipped for reference only, not for reimporting into the
canvas. Reimporting a saved flow that wires a model into an Agent's
Model field trips a real frontend quirk in this Langflow version (the
edge silently drops on reimport, even though the flow runs correctly
via code and the REST API), so Lessons 13, 14, and 16 have you build
that part by hand instead and say so in their own README. Every other
lesson's `flow.json` imports and runs cleanly.

Setup: `GOOGLE_API_KEY` in a `.env` file at the project root (get a free
key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)),
then `uv run python lessons/langflow/<NN>_<name>/lesson.py` from the
project root. Lesson 1 covers starting Langflow itself
(`uv run langflow run`) and opening it in your browser.

## Beginner: building and testing a flow by hand, then headlessly

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_langflow](01_beginner/01_what_is_langflow/) | Install, `langflow run`, the local server, opening the UI |
| 02 | [first_flow](01_beginner/02_first_flow/) | Chat Input -> Gemini -> Chat Output, `Graph`, `.dump()`, `run_flow_from_json` |
| 03 | [components_as_contracts](01_beginner/03_components_as_contracts/) | Typed input/output ports, why the canvas won't let you connect them wrong |
| 04 | [prompt_templates](01_beginner/04_prompt_templates/) | The Prompt component, `{variables}`, wiring one component's output into another |
| 05 | [connecting_and_reordering](01_beginner/05_connecting_and_reordering/) | Edges, execution order, reading a flow's shape off the canvas |
| 06 | [testing_in_the_playground](01_beginner/06_testing_in_the_playground/) | The Playground panel, iterating on inputs without leaving the UI |
| 07 | [global_variables_and_secrets](01_beginner/07_global_variables_and_secrets/) | `GOOGLE_API_KEY` as a global variable, not hardcoded in a component |
| 08 | [session_id_and_memory](01_beginner/08_session_id_and_memory/) | `session_id`, the Memory component, a flow that remembers earlier turns |
| 09 | [beginner_checkpoint_project](01_beginner/09_beginner_checkpoint_project/) | **Checkpoint:** A Small Q&A Flow, Built End to End |

## Intermediate: the code surface, agents, and branching

| # | Lesson | Concept |
|---|--------|---------|
| 10 | [run_flow_from_json_in_depth](02_intermediate/10_run_flow_from_json_in_depth/) | `tweaks`, overriding a component's field for one run without editing `flow.json` |
| 11 | [rest_api_and_auth](02_intermediate/11_rest_api_and_auth/) | `POST /api/v1/run/{flow_id}`, `LANGFLOW_API_KEY`, calling a flow with `httpx` |
| 12 | [custom_component_basics](02_intermediate/12_custom_component_basics/) | Writing a `Component` subclass, `graph.arun()`, no server needed |
| 13 | [custom_component_as_tool](02_intermediate/13_custom_component_as_tool/) | The same component exposed as a tool an Agent can call |
| 14 | [agent_component](02_intermediate/14_agent_component/) | Langflow's built-in Agent component, the tool-calling loop on a canvas |
| 15 | [branching_and_conditional_routing](02_intermediate/15_branching_and_conditional_routing/) | The If-Else/router component, compared to `langgraph`'s conditional edges |
| 16 | [intermediate_checkpoint_project](02_intermediate/16_intermediate_checkpoint_project/) | **Checkpoint:** An Agent Flow With a Custom Tool, Callable Over REST |

## Advanced: production concerns and the prototype-to-code trade-off

| # | Lesson | Concept |
|---|--------|---------|
| 17 | [lfx_headless_execution](03_advanced/17_lfx_headless_execution/) | `lfx`, the lightweight executor, for CI/stateless runs with no server |
| 18 | [screenshotting_the_canvas_with_playwright](03_advanced/18_screenshotting_the_canvas_with_playwright/) | Driving `langflow run` with this repo's own Playwright course pattern |
| 19 | [exporting_and_versioning_flows](03_advanced/19_exporting_and_versioning_flows/) | Git-tracking `flow.json`, why it doesn't diff or code-review like Python |
| 20 | [deploying_a_flow_as_a_service](03_advanced/20_deploying_a_flow_as_a_service/) | `lfx serve`, a standalone API server for one flow, no UI server involved |
| 21 | [webhooks_and_external_triggers](03_advanced/21_webhooks_and_external_triggers/) | The Webhook component, triggering a flow from outside Langflow entirely |
| 22 | [advanced_capstone_project](03_advanced/22_advanced_capstone_project/) | **Capstone:** The Same Small Agent, Langflow vs. Raw LangGraph |
