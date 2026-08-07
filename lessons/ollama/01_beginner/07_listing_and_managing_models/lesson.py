"""
Lesson 7: managing the models on disk, from Python: pull, list, ps, delete.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/ollama/01_beginner/07_listing_and_managing_models/lesson.py

This pulls a small throwaway model (qwen2.5:0.5b, under 500 MB) to
demonstrate deletion, then removes it again at the end, so it doesn't
permanently take up space on your disk.
"""

import ollama

THROWAWAY_MODEL = "qwen2.5:0.5b"


def main() -> None:
    # ollama.pull() is the Python equivalent of `ollama pull` on the CLI.
    # You'd rarely call this at runtime in a real program (Lesson 2 covered
    # why: it's a multi-hundred-MB-to-multi-GB download), but it's useful
    # here to have a disposable model to delete safely.
    print(f"Pulling {THROWAWAY_MODEL} ...")
    ollama.pull(THROWAWAY_MODEL)

    on_disk = [model.model for model in ollama.list().models]
    print(f"\nOn disk now: {on_disk}")

    # ollama.ps() is different from ollama.list(): list() shows everything
    # ever pulled (on disk), ps() shows only what's currently loaded into
    # memory/VRAM right now, the same distinction as "installed" vs
    # "running" for a regular application.
    loaded = ollama.ps().models
    print("\nCurrently loaded in memory:")
    for model in loaded:
        vram_gb = model.size_vram / 1_000_000_000
        print(f"  {model.model} ({vram_gb:.2f} GB in memory, expires {model.expires_at})")

    # ollama.delete() removes a model from disk permanently, the Python
    # equivalent of `ollama rm`. Freeing disk space this way is the main
    # reason to ever call it: unlike a cloud API, a local model you're not
    # using is still costing you gigabytes just sitting there.
    print(f"\nDeleting {THROWAWAY_MODEL} ...")
    ollama.delete(THROWAWAY_MODEL)

    on_disk_after = [model.model for model in ollama.list().models]
    print(f"On disk after delete: {on_disk_after}")


if __name__ == "__main__":
    main()
