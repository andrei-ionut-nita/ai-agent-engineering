"""
Lesson 26: where Agentic RAG hits a wall, and what comes next.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/agentic_rag/03_advanced/26_where_agentic_rag_hits_a_wall/lesson.py
"""


def main() -> None:
    print("This course let the model decide, per question, whether to retrieve,")
    print("how many times, and what else to call instead. Every lesson after")
    print("Lesson 9 made that decision more capable, without changing what the")
    print("model was actually retrieving FROM.\n")

    failure_modes = [
        (
            "Only ever text, still (this whole course, like naive_rag before it)",
            "search_notes() searches plain Markdown notes. This course's agent "
            "can decide WHETHER and HOW OFTEN to retrieve with real "
            "sophistication, but it still has nothing to say about an image, "
            "an audio clip, or a table's structure, the same limit "
            "naive_rag Lesson 26 named, unsolved by adding agency on top.",
            "Multimodal RAG (this series' next course) extends retrieval "
            "across text, images, audio, and video, using embedding spaces "
            "built to compare across content types, not just within one. "
            "An agentic loop deciding WHEN to retrieve is only as capable "
            "as WHAT it can retrieve, and this course never touched that.",
        ),
        (
            "Tool-choice reliability rests entirely on hand-written descriptions (Lessons 4, 16)",
            "Every 'should the model call this tool' decision in this course "
            "traced back to a FunctionDeclaration's description field. "
            "Lesson 16 showed that description steering doesn't fully "
            "prevent unnecessary retrieval, it reduces it, unreliably.",
            "No course in this series fully solves this, it's a genuinely "
            "open problem in how instructable a model's own judgment can be "
            "made through prompting alone, worth carrying forward as an "
            "open question, not a solved one.",
        ),
        (
            "Cost scales with round trips, and the model controls that cost (Lessons 10, 14)",
            "Each loop iteration is a real, billed API call. A well-behaved "
            "question costs one or two; MAX_STEPS bounds the worst case, "
            "but doesn't make a wasteful multi-step question cheap, only "
            "finite.",
            "Adaptive RAG (later in this series) classifies a question's "
            "complexity FIRST, then routes it to however much retrieval "
            "depth it actually needs, shallow and cheap by default, "
            "deeper only when the question earns it.",
        ),
        (
            "No memory of which tool choices actually helped (this whole course)",
            "Lesson 17's evaluation scored retrieve-or-not decisions after "
            "the fact, by hand, once. Nothing in this course's loop learns "
            "from past questions to improve future tool-choice decisions "
            "within a running system.",
            "Outside this series' current scope, an open direction: an "
            "agent that adjusts its own tool descriptions or instructions "
            "based on accumulated evaluation results, not covered here.",
        ),
    ]

    for title, limitation, next_course in failure_modes:
        print(f"- {title}")
        print(f"  Agentic RAG's limit: {limitation}")
        print(f"  Addressed by: {next_course}\n")


if __name__ == "__main__":
    main()
