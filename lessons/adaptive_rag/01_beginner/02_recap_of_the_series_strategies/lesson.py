"""
Lesson 2: no new mechanics, a recap of what each prior course's
strategy is good and bad at, printed as one script.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/01_beginner/02_recap_of_the_series_strategies/lesson.py
"""

STRATEGIES = [
    {
        "name": "Naive RAG",
        "good_at": [
            "single-fact lookup inside one document",
        ],
        "bad_at": [
            "multi-hop questions (naive_rag's own Lesson 16 showed this "
            "failing at k=1)",
            "can be confidently wrong on a scoped search instead of "
            "admitting it doesn't know (naive_rag Lesson 12)",
        ],
    },
    {
        "name": "Hybrid RAG",
        "good_at": [
            "a bare-ID lookup and a paraphrased query, two things naive "
            "retrieval alone missed",
        ],
        "bad_at": [
            "fusion has nothing left to fuse when neither retriever finds "
            "anything relevant",
            "no relevance threshold on the fused result",
            "still confidently wrong on a question whose own premise "
            "doesn't match its answer (hybrid_rag Lesson 16)",
            "no multi-hop reasoning, same ceiling naive RAG has there",
        ],
    },
    {
        "name": "Graph RAG",
        "good_at": [
            "multi-hop questions whose answer lives in a relationship "
            "between entities, not in one passage",
        ],
        "bad_at": [
            "a corrupted or degraded graph produces a well-formed but "
            "silently wrong answer, with no error anywhere (graph_rag "
            "Lesson 16)",
            "no confidence check before answering",
            "fixed traversal depth regardless of how complex the question "
            "actually is",
            "quadratic-cost traversal as the corpus grows (graph_rag "
            "Lesson 19)",
        ],
    },
    {
        "name": "Corrective RAG",
        "good_at": [
            "catching and correcting a bad retrieval before generation "
            "sees it, precision@k jumped from 0.80 to 1.00 in "
            "corrective_rag's own Lesson 17",
        ],
        "bad_at": [
            "grading shares a blind spot with the model doing the "
            "grading (corrective_rag Lesson 16's circularity demo)",
            "bounded correction can still honestly fail",
            "a fixed correction ladder runs identically for every "
            "question, whether or not that question needed correcting "
            "at all",
            "still just one retrieval pass, corrected, not a different "
            "kind of retrieval",
        ],
    },
    {
        "name": "Agentic RAG",
        "good_at": [
            "letting the model decide per question whether to retrieve, "
            "how many times, and what else to call",
        ],
        "bad_at": [
            "never changes WHAT is being searched, still text-only "
            "(agentic_rag Lesson 26)",
            "tool-choice reliability rests on hand-written tool "
            "descriptions, an unsolved problem",
            "model-controlled round trips cost more, each extra call is "
            "a real extra cost",
        ],
    },
]


def main() -> None:
    print("What each prior course's strategy is good and bad at:\n")
    for strategy in STRATEGIES:
        print(f"{strategy['name']}")
        print("  Good at:")
        for point in strategy["good_at"]:
            print(f"    - {point}")
        print("  Bad at:")
        for point in strategy["bad_at"]:
            print(f"    - {point}")
        print()

    print(
        "None of these five is always right. Each one was the best "
        "strategy for the specific failure the course before it ran "
        "into, and each one then ran into its own new failure. This "
        "course's premise: instead of picking one of the five and living "
        "with its blind spot, classify each question first and route it "
        "to whichever strategy actually fits, automatically, per "
        "question."
    )


if __name__ == "__main__":
    main()
