"""
Lesson 12: Node parsers and chunking strategies, contrasting SentenceSplitter
with TokenTextSplitter on the same document.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/llamaindex/02_intermediate/12_node_parsers_and_chunking_strategies/lesson.py

Reuses the Nimbus Robotics remote_work_policy.txt file from Lesson 2
(01_beginner/02_documents_and_nodes/data/). No LLM or embedding calls,
splitting text into Nodes is pure local computation, same as Lesson 2.
"""

from pathlib import Path

from llama_index.core import SimpleDirectoryReader

# SentenceSplitter: already used since Lesson 2. Tries to break chunks on
# sentence boundaries, so a sentence rarely gets cut in half mid-thought.
from llama_index.core.node_parser import SentenceSplitter

# TokenTextSplitter: a plainer alternative. It splits on a target token
# count using a fixed separator (default a single space), with no
# sentence-boundary awareness, closer to a naive fixed-size split than
# SentenceSplitter's sentence-aware one.
from llama_index.core.node_parser import TokenTextSplitter

DATA_DIR = Path(__file__).parent.parent.parent / "01_beginner" / "02_documents_and_nodes" / "data"


def main() -> None:
    documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()
    # Use just the remote work policy for this comparison, one document is
    # enough to see the two parsers diverge, and keeps the printed output
    # readable.
    remote_work_doc = next(
        d for d in documents if Path(d.metadata["file_name"]).name == "remote_work_policy.txt"
    )
    print(f"Document: remote_work_policy.txt, {len(remote_work_doc.text)} characters\n")

    # SentenceSplitter, same chunk_size/chunk_overlap as Lesson 2, but
    # tuned smaller here so a ~1000-character document actually splits
    # into more than one Node, otherwise the comparison would be trivial.
    sentence_splitter = SentenceSplitter(chunk_size=60, chunk_overlap=10)
    sentence_nodes = sentence_splitter.get_nodes_from_documents([remote_work_doc])

    # TokenTextSplitter with the same chunk_size/chunk_overlap budget, so
    # any difference in node count or boundaries comes from the SPLITTING
    # STRATEGY, not from a different size setting.
    token_splitter = TokenTextSplitter(chunk_size=60, chunk_overlap=10)
    token_nodes = token_splitter.get_nodes_from_documents([remote_work_doc])

    print(f"SentenceSplitter (chunk_size=60, chunk_overlap=10): {len(sentence_nodes)} nodes")
    for i, node in enumerate(sentence_nodes):
        preview = node.text.strip().replace("\n", " ")
        print(f"  [{i}] ({len(node.text)} chars) {preview[:70]!r}...")

    print(f"\nTokenTextSplitter (chunk_size=60, chunk_overlap=10): {len(token_nodes)} nodes")
    for i, node in enumerate(token_nodes):
        preview = node.text.strip().replace("\n", " ")
        print(f"  [{i}] ({len(node.text)} chars) {preview[:70]!r}...")

    # The key difference to look for: SentenceSplitter tries to land chunk
    # boundaries on sentence ends (a period followed by whitespace), while
    # TokenTextSplitter's boundaries land wherever the token budget runs
    # out, whatever the separator (a space, by default) allows, sentence
    # or not. Node [8] happens to isolate this cleanly: SentenceSplitter
    # stops exactly at "...for tax and legal reasons." while
    # TokenTextSplitter's corresponding node runs straight through that
    # sentence end into the start of the next sentence.
    sentence_chunk_8 = sentence_nodes[8].text.strip()
    token_chunk_11 = token_nodes[11].text.strip()
    print(f"\nSentenceSplitter node [8]: {sentence_chunk_8!r}")
    print(f"TokenTextSplitter node [11]: {token_chunk_11!r}")
    print(
        "\nSentenceSplitter stopped right at the sentence-ending period; "
        "TokenTextSplitter's token budget ran out mid-way into the next "
        "sentence instead."
    )

    print(
        "\nLangChain comparison: TokenTextSplitter here is the closer analogue "
        "of LangChain's plain CharacterTextSplitter or TokenTextSplitter (a "
        "fixed-size cut with a separator, no structural awareness), while "
        "SentenceSplitter is the closer analogue of RecursiveCharacterTextSplitter "
        "(tries several separators in priority order to avoid cutting "
        "mid-sentence, per Lesson 2's README)."
    )


if __name__ == "__main__":
    main()
