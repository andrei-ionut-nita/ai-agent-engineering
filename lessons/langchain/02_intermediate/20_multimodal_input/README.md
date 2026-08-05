# Lesson 20: Multimodal input, sending an image alongside text

## "Multimodal" just means more than one kind of input

Every message since Lesson 1 has been text: a string, or a `HumanMessage`
wrapping a string. Gemini (like several modern models) can also accept
images as input, alongside text, in the same message. "Multimodal" is
the term for a model that handles more than one type (mode) of input,
here, text and images together.

## Building a test image without downloading anything

```python
image = Image.new("RGB", (200, 100), color="white")
draw = ImageDraw.Draw(image)
draw.rectangle([10, 10, 90, 90], fill="red")
draw.ellipse([110, 10, 190, 90], fill="blue")
```

This uses `Pillow` (`PIL`), a Python image library, to draw a small
picture entirely in code: a white background with a red square and a
blue circle. Generating the image ourselves means this lesson doesn't
depend on any external file or URL, it's fully self-contained and
reproducible.

## Turning the image into something we can send

```python
buffer = io.BytesIO()
image.save(buffer, format="PNG")
base64.b64encode(buffer.getvalue()).decode("utf-8")
```

Images are binary data, not text, but our messages are ultimately sent
as text-based API requests. **Base64** is a standard way of encoding
arbitrary binary data (like an image's bytes) as plain text characters,
so it can travel inside a normal text-based request. This is a general
technique, not a LangChain-specific one, you'll see base64 encoding used
anywhere binary data needs to travel through a text-only channel.

## Building the image content block

```python
image_block = create_image_block(base64=image_base64, mime_type="image/png")
```

`create_image_block` builds the exact structure LangChain expects to
represent image data: the base64-encoded bytes, plus a `mime_type`
telling the model what *kind* of image this is (`"image/png"` here).
Without the correct mime type, the model wouldn't know how to interpret
the bytes.

## A message with mixed content

```python
message = HumanMessage(
    content=[
        {"type": "text", "text": "What two shapes and colors do you see in this image?"},
        image_block,
    ]
)
```

Every `HumanMessage` before this lesson had `content` set to a plain
string. Here, `content` is a **list** of content blocks instead, one
text block and one image block. This is what makes a message
multimodal: instead of one kind of content, it carries several pieces,
of potentially different kinds, together in a single message.

## Proof the model actually looked at it

Run the lesson and the model correctly names both the shape and color
of each object, "a red square" and "a blue circle", details that exist
only in the image, nowhere in the text prompt itself. That's the real
test here: if the model can describe things that were never mentioned
in words, it genuinely processed the image, rather than just responding
to the text question in isolation.

## Running it

```bash
uv run python lessons/langchain/02_intermediate/20_multimodal_input/lesson.py
```

## Checkpoint

- **multimodal**: a model accepting more than one kind of input (here,
  text and images) in the same request.
- **base64 encoding**: turns binary data (like image bytes) into plain
  text characters, so it can travel through a text-based request.
- **content blocks**: a `HumanMessage`'s `content` can be a list of
  differently-typed pieces (text, image, etc.), instead of a single
  plain string.

If anything here still feels unclear, ask before moving to Lesson 21.
