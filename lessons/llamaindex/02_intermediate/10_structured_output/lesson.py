"""
Lesson 10: Structured output, getting a validated Pydantic object back
instead of free text.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/02_intermediate/10_structured_output/lesson.py

Reuses the Nimbus Robotics policy data/ folder from Lesson 2
(01_beginner/02_documents_and_nodes/data/). This lesson builds on Lesson 5's
QueryEngine (01_beginner), the new piece is output_cls: instead of a
QueryEngine handing back a free-text Response, it hands back an instance of
a Pydantic model you define, validated on the way out.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from pydantic import BaseModel, Field

load_dotenv()
API_KEY = os.environ["GOOGLE_API_KEY"]

DATA_DIR = Path(__file__).parent.parent.parent / "01_beginner" / "02_documents_and_nodes" / "data"

Settings.llm = GoogleGenAI(model="gemini-3.5-flash-lite", api_key=API_KEY)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/gemini-embedding-001", api_key=API_KEY)


# A plain Pydantic model describing the shape of the answer we want, not
# the question. A QueryEngine built with output_cls=PolicySummary will
# coerce the LLM's answer into an instance of this class instead of handing
# back free-text Response.response.
class PolicySummary(BaseModel):
    topic: str = Field(description="What policy this summary is about, in a few words")
    max_days: int = Field(description="The maximum number of days mentioned in the policy, as an integer")
    summary: str = Field(description="A one-sentence plain-English summary of the policy")


def main() -> None:
    documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()
    index = VectorStoreIndex.from_documents(documents)

    # Same as_query_engine() call from Lesson 5, plus one new keyword:
    # output_cls. Under the hood this swaps the default free-text response
    # synthesizer for a structured one that asks the LLM to fill in
    # PolicySummary's fields and validates the result against the model
    # before returning it, so a malformed or missing field raises instead
    # of silently returning bad data.
    query_engine = index.as_query_engine(output_cls=PolicySummary)

    response = query_engine.query(
        "Summarize the vacation policy's carryover rule. "
        "What is the maximum number of days involved?"
    )

    # response.response is no longer a plain string, it's an instance of
    # PolicySummary (or, depending on version, a JSON string of it -- we
    # print both the type and the parsed fields to make this concrete).
    print(f"Response type: {type(response.response).__name__}")

    parsed: PolicySummary = response.response
    print(f"\nParsed PolicySummary:")
    print(f"  topic:   {parsed.topic}")
    print(f"  max_days: {parsed.max_days}")
    print(f"  summary: {parsed.summary}")

    # Because it's a real Pydantic object, not text, you get normal Python
    # attribute access and validation, no regex or string-parsing needed
    # to pull max_days back out for use elsewhere in a program.
    print(f"\nmax_days is a {type(parsed.max_days).__name__}: usable directly, e.g. in an if-statement.")

    # Compare with the LLM-direct route from Lesson 3/README: Settings.llm
    # itself can also be wrapped this way, with no index or retrieval
    # involved, useful when you already have the text and just want it
    # coerced into a schema.
    structured_llm = Settings.llm.as_structured_llm(PolicySummary)
    direct = structured_llm.complete(
        "Vacation policy: employees carry over at most 5 unused vacation "
        "days into the next calendar year."
    )
    direct_parsed: PolicySummary = direct.raw
    print(f"\nDirect as_structured_llm() call (no index, no retrieval):")
    print(f"  topic:   {direct_parsed.topic}")
    print(f"  max_days: {direct_parsed.max_days}")
    print(f"  summary: {direct_parsed.summary}")


if __name__ == "__main__":
    main()
