"""
Lesson 18: where your model actually runs, and what quantization trades away.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/03_advanced/18_gpu_vs_cpu_and_quantization/lesson.py
"""

import ollama


def describe_placement(model) -> str:
    if model.size_vram == 0:
        return "fully on CPU (no VRAM used)"
    if model.size_vram == model.size:
        return "fully on GPU (entirely in VRAM)"
    fraction = model.size_vram / model.size
    return f"split, {fraction:.0%} on GPU, the rest on CPU"


def main() -> None:
    # Make sure at least one model is actually loaded before checking.
    ollama.chat(model="llama3.2", messages=[{"role": "user", "content": "hi"}])

    print("Where currently loaded models are actually running:\n")
    for model in ollama.ps().models:
        print(f"  {model.model}: {describe_placement(model)}")

    # size_vram vs size (from Lesson 7's ps() introduction) is the whole
    # story here: if a model's weights don't fit in your GPU's VRAM,
    # Ollama automatically splits it, running part on the GPU and part on
    # the CPU. A CPU-only machine (size_vram always 0) still works, just
    # slower, there's no hard requirement for a GPU at all.

    print("\nQuantization levels of models pulled in this course:")
    for tag in ["llama3.2:1b", "llama3.2"]:
        info = ollama.show(tag)
        print(f"  {tag}: {info.details.quantization_level}, {info.details.parameter_size} parameters")

    # Quantization compresses a model's weights from their original
    # precision (often 16-bit floating point, "fp16") down to fewer bits
    # per number, Q8 (8-bit) or Q4 (4-bit) are common. Fewer bits means
    # less VRAM/RAM needed and faster generation, at the cost of some
    # precision, and therefore some answer quality, though well-chosen
    # quantization (like the Q4_K_M and Q8_0 seen above) keeps that loss
    # small for most everyday use.


if __name__ == "__main__":
    main()
