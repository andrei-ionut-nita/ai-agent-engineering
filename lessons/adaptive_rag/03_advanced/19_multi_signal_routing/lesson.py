"""
Lesson 19: multi-signal routing, three cheap rule-based signals combined
into a complexity score, instead of one LLM classification call.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/adaptive_rag/03_advanced/19_multi_signal_routing/lesson.py
"""

import re

QUESTIONS = [
    "What oven setting does the pizza dough recipe use?",
    "What two hobbies happen in the same room as the weather station?",
    "How does wind speed affect things around the house?",
    "Where does the basil on the pizza come from, and does it also help the tomatoes?",
    "How often does the wind sensor need re-oiling?",
]

# A short list of multi-part / comparison / relationship words. Their
# presence is a cheap signal that a question is reaching across more than
# one fact, the same shape multi-hop questions have had since Lesson 4.
MULTI_PART_WORDS = {"and", "both", "also", "compare", "same", "between", "relationship", "affect", "affects"}


def word_count(query: str) -> int:
    return len(query.split())


def keyword_density(query: str) -> float:
    # Fraction of the question's words that are multi-part / relational
    # signal words. A higher fraction suggests the question is chaining
    # more than one fact together rather than asking for a single one.
    words = re.findall(r"[a-z0-9']+", query.lower())
    if not words:
        return 0.0
    hits = sum(1 for word in words if word in MULTI_PART_WORDS)
    return hits / len(words)


def entity_count(query: str) -> int:
    # A rough, cheap stand-in for named-entity counting: count
    # capitalized words that aren't the first word of the sentence
    # (the first word is capitalized by grammar, not because it names
    # something), plus any standalone capitalized word elsewhere.
    words = query.split()
    count = 0
    for index, word in enumerate(words):
        stripped = word.strip("?,.")
        if stripped and stripped[0].isupper() and index != 0:
            count += 1
    return count


def complexity_score(query: str) -> float:
    # Three cheap, local signals, each normalized to roughly a 0-1
    # range, combined with fixed weights. None of this calls Gemini.
    # A single LLM classification call (Lesson 3) is accurate but costs
    # a round trip every single time, even for a five-word question
    # that's obviously simple. This is where that single-classifier
    # step starts to break down: at scale, paying a full model call for
    # every question, no matter how trivially simple, is wasted cost
    # and wasted latency the multi-signal version below skips entirely
    # for the clear-cut cases.
    length_signal = min(word_count(query) / 20, 1.0)
    density_signal = min(keyword_density(query) * 4, 1.0)
    entity_signal = min(entity_count(query) / 3, 1.0)
    return round(0.3 * length_signal + 0.4 * density_signal + 0.3 * entity_signal, 3)


def label_from_score(score: float) -> str:
    if score < 0.25:
        return "simple_factual"
    if score < 0.55:
        return "ambiguous"
    return "multi_hop"


def main() -> None:
    print("Multi-signal complexity scoring (no Gemini call involved):\n")
    for query in QUESTIONS:
        score = complexity_score(query)
        label = label_from_score(score)
        print(f"Q: {query}")
        print(
            f"   words={word_count(query):<3} density={keyword_density(query):.2f} "
            f"entities={entity_count(query)}  ->  score={score:.3f}  label={label}\n"
        )


if __name__ == "__main__":
    main()
