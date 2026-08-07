"""
Lesson 5: stream a reply token by token instead of waiting for the whole thing.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/01_beginner/05_streaming_responses/lesson.py
"""

import ollama


def main() -> None:
    # stream=True changes the return type: instead of one ChatResponse,
    # ollama.chat() returns an iterator that yields many small ChatResponse
    # chunks as the model generates them, each holding a fragment of text.
    stream = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": "Count from 1 to 5, one number per line."}],
        stream=True,
    )

    chunk_count = 0
    for chunk in stream:
        # print with end="" and flush=True so each fragment appears the
        # instant it arrives, instead of Python buffering output until a
        # full line is ready.
        print(chunk.message.content, end="", flush=True)
        chunk_count += 1
        # The final chunk in the stream has done=True and empty content,
        # it's a signal, not more text.
        if chunk.done:
            break

    print(f"\n\n(received {chunk_count} chunks)")


if __name__ == "__main__":
    main()
