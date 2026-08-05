"""
Lesson 17: graph-based control flow with pydantic_graph.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/pydantic_ai/02_intermediate/17_graph_based_agents_with_pydantic_graph/lesson.py

Requires GOOGLE_API_KEY in a .env file at the project root.
"""

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_graph import GraphBuilder, StepContext

load_dotenv()

agent = Agent(
    "google:gemini-3.5-flash-lite",
    system_prompt="Write one short joke about the given topic.",
)

builder = GraphBuilder(input_type=str, output_type=str)


@builder.step
async def write_joke(ctx: StepContext[None, None, str]) -> str:
    result = await agent.run(ctx.inputs)
    return result.output


@builder.step
async def add_rimshot(ctx: StepContext[None, None, str]) -> str:
    return ctx.inputs + "\n*rimshot*"


builder.add_edge(builder.start_node, write_joke)
builder.add_edge(write_joke, add_rimshot)
builder.add_edge(add_rimshot, builder.end_node)

graph = builder.build()


def main() -> None:
    result = graph.run_sync(inputs="cats")
    print(result)


if __name__ == "__main__":
    main()
