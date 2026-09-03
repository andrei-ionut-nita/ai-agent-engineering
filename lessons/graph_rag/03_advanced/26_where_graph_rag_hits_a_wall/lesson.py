"""
Lesson 26: where Graph RAG hits a wall, and what comes next.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/03_advanced/26_where_graph_rag_hits_a_wall/lesson.py
"""


def main() -> None:
    print("This course built Graph RAG by hand: extract, build, traverse, generate.")
    print("Every lesson after Lesson 9 made one piece of that pipeline more honest")
    print("about its own limits, without changing the underlying architecture.\n")

    failure_modes = [
        (
            "Extraction errors compound silently (Lesson 16)",
            "A wrong or missing triple at hop 1 doesn't raise an error, it "
            "just quietly corrupts every answer whose reasoning needed to "
            "pass through that hop, with the gathered facts looking "
            "completely well-formed the whole time.",
            "Corrective RAG (CRAG) adds a grading step: retrieved evidence "
            "is evaluated for relevance and support before generation ever "
            "sees it, so a bad retrieval gets caught, not answered from "
            "anyway.",
        ),
        (
            "No confidence check before answering (Lessons 22, 23, 25)",
            "This course's ask() always traverses from whatever starting "
            "node chromadb's top-1 match returns, with no check on whether "
            "that match was actually a good one.",
            "Corrective RAG grades the retrieved evidence directly, and "
            "routes to a fallback strategy when the grade is low, instead "
            "of generating from a possibly-wrong starting point regardless.",
        ),
        (
            "Fixed traversal depth, regardless of question complexity (Lesson 14)",
            "This course tuned max_hops once and used it for every "
            "question; a question needing one hop and a question needing "
            "four both get the same depth.",
            "Adaptive RAG classifies a query first, then routes it to "
            "however much retrieval depth that specific question actually "
            "needs, shallow for simple questions, deeper for hard ones.",
        ),
        (
            "One-shot traversal, no re-attempt (every lesson)",
            "This course's traversal always runs exactly once, from one "
            "starting node, for a fixed number of hops; there's no "
            "mechanism to try a different starting entity if the first "
            "attempt comes up short.",
            "Agentic RAG lets a model decide whether, what, and how many "
            "times to retrieve, planning its own research instead of "
            "following one fixed pipeline every time.",
        ),
        (
            "Graphs that only ever model text (this whole course)",
            "Every entity and relationship in this course's graph came "
            "from plain Markdown notes; nothing here extracts relationships "
            "from an image, a table, or an audio transcript.",
            "Multimodal RAG extends retrieval (and, in principle, "
            "extraction) across text, images, audio, and video, not just "
            "within one content type.",
        ),
    ]

    for title, limitation, next_course in failure_modes:
        print(f"- {title}")
        print(f"  Graph RAG's limit: {limitation}")
        print(f"  Addressed by: {next_course}\n")


if __name__ == "__main__":
    main()
