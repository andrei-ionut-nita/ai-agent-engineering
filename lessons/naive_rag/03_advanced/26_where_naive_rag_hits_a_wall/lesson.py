"""
Lesson 26: where Naive RAG hits a wall, and what comes next.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/naive_rag/03_advanced/26_where_naive_rag_hits_a_wall/lesson.py
"""


def main() -> None:
    print("This course built Naive RAG by hand: chunk, embed, retrieve, generate.")
    print("Every lesson after Lesson 8 made one piece of that pipeline more honest")
    print("about its own limits, without changing the underlying architecture.\n")

    failure_modes = [
        (
            "Multi-hop questions (Lesson 16)",
            "A single similarity search has no way to know a question needs "
            "information from more than one place, or to go looking for a "
            "second piece once it finds the first.",
            "Graph RAG models explicit relationships between pieces of "
            "information, so a multi-hop question can be answered by "
            "traversing connections, not just ranking passages in isolation.",
        ),
        (
            "Retrieval that's confidently wrong (Lessons 12, 14, 22)",
            "Top-k similarity search always returns its best available "
            "match, even when 'best available' still isn't good enough, "
            "a threshold catches the worst cases, not the subtle ones.",
            "Corrective RAG (CRAG) adds a grading step: retrieved documents "
            "are evaluated before generation, and a low grade triggers a "
            "different strategy instead of answering from bad context anyway.",
        ),
        (
            "One-shot retrieval, no matter the question (every lesson)",
            "This course's retrieve() always runs exactly once, with a "
            "fixed k, whether the question is simple or genuinely needs "
            "several rounds of looking things up.",
            "Agentic RAG lets a model decide whether, what, and how many "
            "times to retrieve, planning its own research instead of "
            "following one fixed pipeline every time.",
        ),
        (
            "Only ever text (this whole course)",
            "Every fixture in this course has been plain text or Markdown; "
            "naive chunk-and-embed has nothing to say about an image, an "
            "audio clip, or a table's structure.",
            "Multimodal RAG extends retrieval across text, images, audio, "
            "and video, using embedding spaces built to compare across "
            "content types, not just within one.",
        ),
        (
            "Same k, every question, regardless of complexity",
            "This course fixed k at 1 or 2 throughout, a simple factual "
            "question and a sprawling comparative one get the same amount "
            "of retrieved context either way.",
            "Adaptive RAG classifies a query first, then routes it to "
            "however much retrieval depth that specific question actually "
            "needs, cheap and shallow for simple questions, deeper for hard ones.",
        ),
    ]

    for title, limitation, next_course in failure_modes:
        print(f"- {title}")
        print(f"  Naive RAG's limit: {limitation}")
        print(f"  Addressed by: {next_course}\n")


if __name__ == "__main__":
    main()
