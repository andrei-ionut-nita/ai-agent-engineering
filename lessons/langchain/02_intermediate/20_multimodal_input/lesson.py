"""
Lesson 20: multimodal input, sending an image alongside text.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langchain/02_intermediate/20_multimodal_input/lesson.py

Every lesson so far has sent text only. Gemini can also read images.
This lesson generates a tiny image with Python (so nothing external
needs downloading), sends it to the model alongside a question, and
checks the model actually looked at it rather than guessing.
"""

import base64
import io

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.messages.content import create_image_block
from langchain_google_genai import ChatGoogleGenerativeAI
from PIL import Image, ImageDraw

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


def make_test_image() -> str:
    """Draw a small image: a red square next to a blue circle, on a
    white background. Returns it as a base64-encoded PNG string."""
    image = Image.new("RGB", (200, 100), color="white")
    draw = ImageDraw.Draw(image)
    draw.rectangle([10, 10, 90, 90], fill="red")
    draw.ellipse([110, 10, 190, 90], fill="blue")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def main() -> None:
    image_base64 = make_test_image()

    # create_image_block() builds the content block LangChain expects
    # for image data. "base64" holds the encoded image bytes, "mime_type"
    # tells the model what kind of image it is (a PNG here).
    image_block = create_image_block(base64=image_base64, mime_type="image/png")

    # A HumanMessage's content can be a LIST of content blocks instead
    # of a single string, mixing text and non-text pieces in one
    # message, this is what makes it "multimodal."
    message = HumanMessage(
        content=[
            {"type": "text", "text": "What two shapes and colors do you see in this image?"},
            image_block,
        ]
    )

    response = model.invoke([message])
    print("Model's description:", response.text)


if __name__ == "__main__":
    main()
