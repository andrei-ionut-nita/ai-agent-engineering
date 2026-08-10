"""
Lesson 19: Workflows, the event-driven engine under QueryEngine and FunctionAgent.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/03_advanced/19_workflows/lesson.py

Every QueryEngine and every FunctionAgent used so far in this course is,
under the hood, a Workflow: a small graph of steps that pass typed Events
to each other. This lesson hand-rolls a tiny retrieve -> synthesize
pipeline as its own Workflow subclass, to make that mechanism visible
instead of hidden behind index.as_query_engine().
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

DATA_DIR = Path(__file__).parent.parent.parent / "01_beginner" / "02_documents_and_nodes" / "data"

Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)

# Build the index once at module level; the Workflow below queries it,
# it doesn't build it, this lesson is about workflow mechanics, not
# indexing (already covered in Lesson 4).
documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()
index = VectorStoreIndex.from_documents(documents)


# A custom Event subclass, the payload passed from the "retrieve" step to
# the "synthesize" step. Events are how steps in a Workflow talk to each
# other: a step's return type tells the Workflow which step(s) can run
# next, since the next step's signature says which Event type it accepts.
class RetrievedEvent(Event):
    query: str
    context: str
    num_nodes: int


# A second custom Event, letting us split "synthesize" into its own step
# rather than cramming everything into one. Small pipelines like this
# usually have as many Event types as there are hand-offs between steps.
class SynthesizedEvent(Event):
    answer: str
    num_nodes: int


class SimpleRagWorkflow(Workflow):
    # @step marks a method as a node in the workflow graph. Its parameter
    # type (StartEvent here) says what triggers it; its return type
    # (RetrievedEvent) says what it hands off next. StartEvent is the
    # built-in entry point, whatever kwargs get passed to .run() show up
    # as attributes on it.
    @step
    async def retrieve(self, ev: StartEvent) -> RetrievedEvent:
        query = ev.query
        retriever = index.as_retriever(similarity_top_k=2)
        nodes = retriever.retrieve(query)
        context = "\n\n".join(node.get_content() for node in nodes)
        return RetrievedEvent(query=query, context=context, num_nodes=len(nodes))

    # This step only runs once a RetrievedEvent exists, the Workflow reads
    # that off the type annotation, no manual wiring or graph-building
    # code needed the way you'd write StateGraph edges in LangGraph.
    @step
    async def synthesize(self, ev: RetrievedEvent) -> SynthesizedEvent:
        prompt = (
            f"Answer the question using only the context below.\n\n"
            f"Context:\n{ev.context}\n\nQuestion: {ev.query}\nAnswer:"
        )
        response = await Settings.llm.acomplete(prompt)
        return SynthesizedEvent(answer=response.text.strip(), num_nodes=ev.num_nodes)

    # StopEvent is the built-in exit point. Whatever is passed as
    # result= becomes the return value of workflow.run().
    @step
    async def finalize(self, ev: SynthesizedEvent) -> StopEvent:
        return StopEvent(result={"answer": ev.answer, "num_nodes": ev.num_nodes})


async def run_workflow(query: str) -> None:
    workflow = SimpleRagWorkflow(timeout=60, verbose=False)
    # kwargs passed to .run() become attributes on the StartEvent that
    # kicks off the graph, here that's the single query= kwarg the
    # retrieve() step reads as ev.query.
    result = await workflow.run(query=query)
    print(f"Q: {query}")
    print(f"A: {result['answer']}")
    print(f"  (synthesized from {result['num_nodes']} retrieved nodes)\n")


def main() -> None:
    import asyncio

    print("Hand-rolled 3-step Workflow: retrieve -> synthesize -> finalize\n")
    print("(This is the same shape of work index.as_query_engine() does for")
    print("you automatically, made visible as explicit steps and events.)\n")

    asyncio.run(run_workflow("What is Nimbus Robotics' policy on remote work equipment?"))


if __name__ == "__main__":
    main()
