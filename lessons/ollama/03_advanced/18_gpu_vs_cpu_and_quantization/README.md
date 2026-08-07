# Lesson 18: GPU vs CPU, and Quantization

## Two separate levers on the same problem

Local inference speed comes down to two mostly-independent decisions:
where the model runs (GPU vs CPU) and how compressed its weights are
(quantization). Both trade some resource for some speed, this lesson
covers each in turn.

## GPU vs CPU: where the math actually happens

A GPU can do the matrix multiplication at the heart of running a model
far faster than a CPU, but only if the model's weights fit in the
GPU's own fast memory (VRAM). Ollama handles this automatically: if a
model fits entirely in your available VRAM, it runs entirely on GPU;
if it doesn't fit, Ollama splits it, some layers on GPU, the rest on
CPU; if you have no usable GPU at all, everything runs on CPU. No
configuration is required for any of this, though it does mean your
hardware, not your code, is often the real bottleneck on speed.

```python
model.size_vram == 0        # fully on CPU
model.size_vram == model.size   # fully on GPU
0 < model.size_vram < model.size  # split between both
```

`ollama.ps()`, from Lesson 7, already reports both numbers, `size` is
the model's total footprint, `size_vram` is how much of that is
currently sitting in GPU memory. Comparing the two tells you exactly
where a loaded model is running, without needing any GPU-specific
tooling.

## Quantization: compressing the weights themselves

A model's weights are numbers, originally often stored at 16 bits of
precision each (`fp16`). Quantization rounds those numbers to fewer
bits, `Q8_0` (8-bit) or `Q4_K_M` (4-bit, "K_M" describing a mixed
precision scheme within that) are common choices you've already seen
in `ollama.show()`'s output since Lesson 2. Fewer bits per number
means a smaller file, less VRAM/RAM needed, and faster generation, at
the cost of some numerical precision.

In practice, well-chosen quantization (the community has done a lot of
work tuning schemes like `Q4_K_M`) keeps quality loss small for most
everyday use, which is exactly why Ollama's default pulls are already
quantized rather than full-precision. Going further down, to `Q2` or
similar, trades away noticeably more quality for a smaller footprint
still, useful on very constrained hardware, not a first choice
otherwise.

## Running it

```bash
uv run python lessons/ollama/03_advanced/18_gpu_vs_cpu_and_quantization/lesson.py
```

## Expected output

The exact placement and which models appear depends entirely on your
hardware and what's currently loaded, on a machine with enough VRAM,
you'll see everything fully on GPU:

```
Where currently loaded models are actually running:

  llama3.2:latest: fully on GPU (entirely in VRAM)
  llama3.2:1b: fully on GPU (entirely in VRAM)
  llama3:latest: fully on GPU (entirely in VRAM)

Quantization levels of models pulled in this course:
  llama3.2:1b: Q8_0, 1.2B parameters
  llama3.2: Q4_K_M, 3.2B parameters
```

On a CPU-only machine, every line under "Where currently loaded models
are actually running" would instead say "fully on CPU", generation
would still work, just slower, matching what Lesson 15 already showed
you about the size/speed tradeoff.

## Checkpoint

- **GPU vs CPU**: Ollama automatically places a model based on
  available VRAM, no configuration needed, CPU-only machines still work.
- **`size_vram` vs `size`**: comparing the two tells you exactly where
  a loaded model is running.
- **Quantization**: compresses weights to fewer bits per number,
  smaller and faster, at some cost to precision.
- **`Q4_K_M` / `Q8_0`**: common, well-tuned quantization schemes that
  keep quality loss small for everyday use.

If anything here still feels unclear, ask before moving to Lesson 19.
