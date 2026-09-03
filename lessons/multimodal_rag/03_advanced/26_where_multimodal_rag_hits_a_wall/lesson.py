"""
Lesson 26: no code, a bridge to the next course in this series.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/multimodal_rag/03_advanced/26_where_multimodal_rag_hits_a_wall/lesson.py
"""

LIMITATIONS = [
    (
        "Captions are a lossy, one-time summary of an image (Lesson 15). "
        "A detail the caption's author didn't think to mention becomes "
        "permanently unretrievable, even though the original image still has it.",
        "Joint embedding spaces (CLIP-style models, named but not built in "
        "Lesson 1) embed pixels directly, no lossy text summary in between.",
    ),
    (
        "Re-attaching the original image at generation time is a per-query "
        "vision call, paid every time that image is retrieved (Lesson 19), "
        "not once like captioning.",
        "Caching generation answers (not just captions) per image and "
        "question type, out of scope in this course.",
    ),
    (
        "Every ask(query, state, k) call in this course used a k chosen in "
        "advance, the same depth regardless of whether a question needed "
        "one fact or several.",
        "Adaptive RAG (this series' next course): decide k, or whether to "
        "retrieve at all, per question.",
    ),
    (
        "Retrieval only ever ran once per question; if the top-k results "
        "were a bad match, this course had no way to notice and try again.",
        "Agentic RAG: an agent that can inspect its own retrieval and "
        "decide to search again with a different query.",
    ),
]


def main() -> None:
    print("Where Multimodal RAG hits a wall:\n")
    for i, (limitation, addressed_by) in enumerate(LIMITATIONS, start=1):
        print(f"{i}. {limitation}")
        print(f"   -> {addressed_by}\n")

    print(
        "This course's ingest()/ask() (Lesson 22) implements this series' "
        "shared Strategy protocol, so Adaptive RAG's routing layer can wire "
        "it in directly, without reading this course's full implementation.\n"
    )
    print("Congratulations on completing the course.")


if __name__ == "__main__":
    main()
