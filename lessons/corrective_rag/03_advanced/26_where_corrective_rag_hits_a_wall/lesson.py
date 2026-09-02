"""
Lesson 26: Where Corrective RAG Hits a Wall.

No code today, this is the last lesson, and it's a bridge, not a
capstone. This script prints a summary of specific limits this course
ran into along the way, each paired with what motivates Agentic RAG,
the next course in this series.

Read README.md in this folder first, then run this with:

    uv run python lessons/corrective_rag/03_advanced/26_where_corrective_rag_hits_a_wall/lesson.py
"""


LIMITS = [
    (
        "Grading is only ever as independent as the model doing it",
        "Lesson 16",
        "the grader shares the generator's model family, and a fabricated "
        "but confidently-worded passage fooled both the same way",
    ),
    (
        "Correction is bounded, on purpose, which means it can still fail",
        "Lesson 21",
        "a bounded rewrite loop gives up cleanly instead of looping "
        "forever, but 'gives up cleanly' is still 'gives up'",
    ),
    (
        "The correction strategy is fixed in advance, not chosen per question",
        "Lessons 6-7, 14, 22",
        "this course always tries the same fallback ladder (filter, "
        "rewrite, external search), a harder or more unusual question "
        "gets no more effort than an easy one",
    ),
    (
        "One retrieval pass, corrected, is still one retrieval pass",
        "Lessons 8-9",
        "this course's whole pipeline runs once per question, it never "
        "decides mid-answer that it needs to look something up again",
    ),
]


def main() -> None:
    print("Five lessons in, this course built a real fix for naive RAG's")
    print("confidently-wrong retrieval. It also ran into its own limits,")
    print("each one demonstrated hands-on, not just described:\n")

    for i, (limit, lesson, detail) in enumerate(LIMITS, start=1):
        print(f"{i}. {limit}")
        print(f"   Demonstrated in: {lesson}")
        print(f"   {detail}\n")

    print(
        "Agentic RAG (course 5 in this series) is what addresses the last "
        "two directly: instead of one fixed correction ladder run once per "
        "question, an agent decides, per question, whether to retrieve "
        "again, which tool to use, and when it actually has enough to "
        "answer. Corrective RAG's grading and correction steps don't "
        "disappear there, they become tools an agent can choose to call, "
        "rather than a fixed sequence every question runs through "
        "identically."
    )


if __name__ == "__main__":
    main()
