"""
Lesson 26: series retrospective, no new code.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/03_advanced/26_series_retrospective/lesson.py
"""


def main() -> None:
    print("Seven courses, one series, organized by RAG architecture instead of")
    print("by library. Each course added exactly one capability on top of the")
    print("one before it, because it ran into a specific limit the prior course")
    print("couldn't solve.\n")

    chain = [
        (
            "1. Naive RAG",
            "Chunk, embed, retrieve, generate, built by hand: raw Gemini "
            "calls, a plain list as the vector store, manual cosine "
            "similarity, graduating to chromadb.",
            "One similarity search per question, so a multi-hop question "
            "has no way to gather information from more than one place.",
        ),
        (
            "2. Hybrid RAG",
            "Dense (embedding) retrieval combined with sparse (keyword) "
            "retrieval, fused into one ranked result.",
            "Fusion can only combine what both retrievers found, together, "
            "in one place, it still has no notion of a relationship "
            "between two separate facts.",
        ),
        (
            "3. Graph RAG",
            "Explicit relationships between facts, extracted into a "
            "knowledge graph, answered by traversal instead of ranking "
            "passages in isolation.",
            "A traversal can be well-formed, complete, and still simply "
            "wrong, with nothing in the pipeline noticing.",
        ),
        (
            "4. Corrective RAG",
            "A grading step before generation: retrieved context is "
            "evaluated, and a low grade triggers correction instead of "
            "answering from bad context anyway.",
            "One fixed correction ladder, run identically for every "
            "question, whether that question needed correcting or not.",
        ),
        (
            "5. Agentic RAG",
            "Retrieval as a tool the model chooses to call, with its own "
            "judgment, instead of a hardcoded pipeline step.",
            "Every tool in this course's registry only ever searched "
            "text, an image or a table was invisible to it.",
        ),
        (
            "6. Multimodal RAG",
            "Retrieval extended across text and images, captioning-then-"
            "embed, reusing the same pipeline every prior course already "
            "built.",
            "A fixed retrieval depth for every question, a simple lookup "
            "and a sprawling comparative question got the same k either "
            "way.",
        ),
        (
            "7. Adaptive RAG (this course)",
            "A classifier routes each question to whichever of the six "
            "strategies above actually fits it, wiring in courses 2 "
            "through 5's real Advanced-tier implementations behind one "
            "router.",
            "Its own routing rules are tuned against the same mixed "
            "question set Lesson 17 evaluates against, train/test "
            "contamination this course names rather than hides.",
        ),
    ]

    for title, added, limit in chain:
        print(f"- {title}")
        print(f"  Added: {added}")
        print(f"  Ran into: {limit}\n")

    print(
        "Five of the six prior courses plug into this course's router "
        "without modification (Lesson 21), because every one of them "
        "shares the same ingest() -> State / ask(query, state, k) -> str "
        "shape. That only works because each course was honest about its "
        "own limit in its own closing lesson, so the next course always "
        "knew exactly what problem it existed to solve."
    )


if __name__ == "__main__":
    main()
