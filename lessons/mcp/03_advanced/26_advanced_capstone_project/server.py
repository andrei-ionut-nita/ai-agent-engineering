"""
Advanced capstone: a Task Manager MCP server combining every server-side
concept from this course: tools, a resource, a prompt, lifespan-managed
state (Lesson 18), proper error handling (Lesson 7), stderr-safe
logging (Lesson 8), and a choice of stdio or Streamable HTTP transport
(Lesson 20), selected on the command line.

Run over stdio (the default, what lesson.py uses):
    uv run python lessons/mcp/03_advanced/26_advanced_capstone_project/server.py

Run over HTTP instead:
    uv run python lessons/mcp/03_advanced/26_advanced_capstone_project/server.py --transport streamable-http
"""

import argparse
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

from mcp.server.fastmcp import Context, FastMCP

logger = logging.getLogger(__name__)


@dataclass
class TaskManagerState:
    tasks: dict[int, dict] = field(default_factory=dict)
    next_id: int = 1


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[TaskManagerState]:
    logger.info("Task Manager server starting up")
    yield TaskManagerState()
    logger.info("Task Manager server shutting down")


mcp = FastMCP("task-manager-server", port=8933, stateless_http=True, lifespan=lifespan)


@mcp.tool()
def add_task(description: str, ctx: Context) -> int:
    """Add a task and return its id."""
    state: TaskManagerState = ctx.request_context.lifespan_context
    task_id = state.next_id
    state.tasks[task_id] = {"description": description, "done": False}
    state.next_id += 1
    logger.info("Added task %s", task_id)
    return task_id


@mcp.tool()
def complete_task(task_id: int, ctx: Context) -> str:
    """Mark a task as done."""
    state: TaskManagerState = ctx.request_context.lifespan_context
    if task_id not in state.tasks:
        raise ValueError(f"No task with id {task_id}.")
    state.tasks[task_id]["done"] = True
    logger.info("Completed task %s", task_id)
    return f"Task {task_id} marked done."


@mcp.tool()
def list_tasks(ctx: Context) -> dict[int, dict]:
    """List every task currently tracked, by id."""
    state: TaskManagerState = ctx.request_context.lifespan_context
    return dict(state.tasks)


@mcp.resource("tasks://{task_id}")
def read_task(task_id: str, ctx: Context) -> str:
    """Read a single task's details by id."""
    state: TaskManagerState = ctx.request_context.lifespan_context
    parsed_id = int(task_id)
    if parsed_id not in state.tasks:
        return f"No task with id {parsed_id}."
    task = state.tasks[parsed_id]
    status = "done" if task["done"] else "pending"
    return f"Task {parsed_id} ({status}): {task['description']}"


@mcp.prompt()
def summarize_tasks() -> str:
    """Ask a model to summarize the current task list."""
    return "Please summarize the current tasks, grouped by pending vs done."


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", choices=["stdio", "streamable-http"], default="stdio")
    args = parser.parse_args()
    mcp.run(transport=args.transport)
