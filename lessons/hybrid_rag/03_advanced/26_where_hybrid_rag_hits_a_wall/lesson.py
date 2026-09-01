"""
Lesson 26: where Hybrid RAG hits a wall, and what comes next.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/hybrid_rag/03_advanced/26_where_hybrid_rag_hits_a_wall/lesson.py
"""


def main() -> None:
    print("This course built Hybrid RAG by hand: two independent retrievers,")
    print("dense and sparse, fused by rank instead of by score. Every lesson")
    print("after Lesson 9 made the fusion more robust without changing the")
    print("underlying idea: two single-shot rankings, combined once, per query.\n")

    failure_modes = [
        (
            "Fusion can't invent signal neither retriever found (Lesson 16)",
            "RRF only ever recombines existing rankings. When a question's "
            "own premise doesn't match its answer, both dense and sparse "
            "can independently rank the right document last, and there is "
            "no floor to catch that, fusion has nothing to fuse it up from.",
            "Corrective RAG (course 4) adds a grading step after retrieval: "
            "a low-confidence result triggers query rewriting and "
            "re-retrieval, instead of answering from whatever fusion "
            "happened to produce.",
        ),
        (
            "Still no relevance threshold (Lesson 25's capstone)",
            "This course's service always answers from its fused top-k, "
            "confidently, even when neither retriever ranked the right "
            "document highly. Nothing downstream checks whether the "
            "retrieved context is actually good enough to answer from.",
            "Corrective RAG's grading step is exactly this missing check, "
            "applied after retrieval instead of assumed away.",
        ),
        (
            "Still one-shot, still no multi-hop (this whole course)",
            "Dense and sparse retrieval, fused or not, both run exactly "
            "once per question and both only ever look inside individual "
            "chunks. A question needing facts connected across two "
            "documents has no mechanism here to gather both.",
            "Graph RAG (course 3, next in this series) models explicit "
            "relationships between pieces of information, so a multi-hop "
            "question can be answered by traversing connections, not by "
            "ranking isolated passages, however those rankings are fused.",
        ),
        (
            "Fixed k, fixed retrieval depth, every question (this whole course)",
            "A bare-ID lookup and a genuinely hard, ambiguous question get "
            "exactly the same k and exactly one retrieval pass, this "
            "course never asks whether a question needs more.",
            "Agentic RAG lets a model decide whether, what, and how many "
            "times to retrieve, instead of following one fixed pipeline, "
            "hybrid or not, every time.",
        ),
    ]

    for title, limitation, next_course in failure_modes:
        print(f"- {title}")
        print(f"  Hybrid RAG's limit: {limitation}")
        print(f"  Addressed by: {next_course}\n")


if __name__ == "__main__":
    main()
