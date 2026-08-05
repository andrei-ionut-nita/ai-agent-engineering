"""
Lesson 9: stream_mode="messages", token-by-token streaming from a node.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langgraph/01_beginner/09_streaming_tokens/lesson.py

New here: streaming reaches inside a node's model call and yields
pieces of the reply as they're generated, instead of waiting for the
whole node (Lesson 8's "values"/"updates") to finish. Same one-node
graph as Lesson 6, only how we run it changes.
"""

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import END, START, MessagesState, StateGraph

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


def call_model(state: MessagesState) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("call_model", call_model)
builder.add_edge(START, "call_model")
builder.add_edge("call_model", END)

app = builder.compile()


def main() -> None:
    print("Streaming answer token by token:\n")

    # stream_mode="messages" yields (token_chunk, metadata) pairs as the
    # model generates its reply inside call_model, not once call_model
    # is entirely done. metadata tells you which node/call produced
    # this piece, handy once a graph has more than one model-calling node.
    for token_chunk, metadata in app.stream(
        {"messages": [HumanMessage("Explain graphs in three short sentences.")]},
        stream_mode="messages",
    ):
        # end="" so tokens print side by side instead of one per line,
        # flush=True so each piece appears immediately instead of being
        # buffered, which would defeat the point of streaming.
        print(token_chunk.text, end="", flush=True)

    print("\n\n(streamed from node:", metadata["langgraph_node"], ")")


if __name__ == "__main__":
    main()
