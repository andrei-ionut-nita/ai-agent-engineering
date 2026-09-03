"""
Lesson 3: extracting named entities from a document by prompting Gemini.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/graph_rag/01_beginner/03_extracting_entities_by_hand/lesson.py
"""

import json
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

CHAT_MODEL = "gemini-3.5-flash-lite"
NOTES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "notes"

SOURCE_FILES = ["greenhouse.md", "maintenance-log.md"]


def extract_entities(text: str) -> list[str]:
    prompt = f"""You are extracting entities for a knowledge graph.

Read the text below and list every named entity: specific people (by
name), specific places, and specific things or objects that another
sentence could plausibly refer back to (for example "humidity sensor",
"greenhouse", "multimeter"). Do not include entities not mentioned in
the text. Do not include abstract concepts, dates, or generic actions.

Return ONLY a JSON array of short strings, one per entity, using each
entity's most natural short name. Example format:
["Dev", "greenhouse", "humidity sensor"]

Text:
{text}"""
    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json", temperature=0
        ),
    )
    assert response.text is not None
    return json.loads(response.text)


def main() -> None:
    for filename in SOURCE_FILES:
        text = (NOTES_DIR / filename).read_text()
        entities = extract_entities(text)
        print(f"--- {filename} ---")
        print(entities)
        print()


if __name__ == "__main__":
    main()
