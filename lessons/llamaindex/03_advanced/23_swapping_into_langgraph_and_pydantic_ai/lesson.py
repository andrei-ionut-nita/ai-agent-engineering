"""
Lesson 23: Wrapping a LlamaIndex query engine as a tool inside LangGraph.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/03_advanced/23_swapping_into_langgraph_and_pydantic_ai/lesson.py

Mirrors lessons/ollama/02_intermediate/13_swapping_into_langchain (dropping
one framework's model into another) and lessons/langchain/03_advanced/29_rag_as_a_tool
(wrapping retrieval as a @tool an agent decides to call). This lesson
combines both ideas: a LlamaIndex QueryEngine, built entirely with
LlamaIndex's own vocabulary (Settings, VectorStoreIndex), gets wrapped as
a plain Python function and handed to a LangChain/LangGraph agent
(create_agent, the same function lesson 29 used), so that agent can
decide for itself when a question needs the Nimbus policy documents.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

DATA_DIR = Path(__file__).parent.parent.parent / "01_beginner" / "02_documents_and_nodes" / "data"

# LlamaIndex's own Settings, exactly as every other lesson in this course
# configures it. Nothing about building this index or query engine knows
# or cares that a LangChain agent will end up calling it.
Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)

documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine(similarity_top_k=2)


# Same @tool decorator langchain Lesson 13 and Lesson 29 used. The body
# is one line, query_engine.query(...), everything LlamaIndex does
# internally (embed the question, retrieve nodes, synthesize an answer)
# stays entirely inside LlamaIndex; LangChain only ever sees a plain
# Python function that takes a string and returns a string.
@tool
def search_nimbus_policies(question: str) -> str:
    """Search Nimbus Robotics' internal policy documents (vacation, remote
    work, and expense policies) to answer a question about company policy.
    Use this for anything that sounds like an HR or expense policy
    question, not for general knowledge questions."""
    response = query_engine.query(question)
    return str(response.response)


# A SEPARATE model object for the LangGraph/LangChain agent layer,
# ChatGoogleGenerativeAI rather than GoogleGenAI. This is the crux of the
# lesson: the two frameworks don't share a model object, LlamaIndex's
# Settings.llm and LangChain's model= are two different instances of
# (functionally) the same Gemini model, each configured the normal way
# for its own framework. The only thing crossing the boundary between
# them is the plain function above.
agent_model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
agent = create_agent(
    model=agent_model,
    tools=[search_nimbus_policies],
    system_prompt=(
        "You are a helpful assistant. Use the search_nimbus_policies tool "
        "for any question about Nimbus Robotics' internal policies."
    ),
)


def ask(question: str) -> None:
    result = agent.invoke({"messages": [HumanMessage(question)]})
    print(f"Q: {question}")
    print(f"A: {result['messages'][-1].text}\n")


def main() -> None:
    # This can only be answered correctly by actually calling the
    # LlamaIndex-backed tool, the agent has no other way to know it.
    ask("How much notice do I need to give before taking vacation at Nimbus Robotics?")

    # General knowledge, no tool needed, showing the agent still knows
    # when NOT to reach for the policy search, same check Lesson 29 ran.
    ask("What is the capital of France?")

    print(
        "The same pattern applies to Pydantic AI: instead of @tool + create_agent, "
        "you'd decorate a function with @agent.tool on a pydantic_ai.Agent, and its "
        "body would still be exactly one line, query_engine.query(...). Either "
        "framework works as the 'outer' agent; only the tool-registration syntax "
        "changes, the LlamaIndex query engine underneath is untouched."
    )


if __name__ == "__main__":
    main()
