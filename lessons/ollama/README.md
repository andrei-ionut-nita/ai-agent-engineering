# Course index

A linear, one-concept-per-lesson path through **Ollama**, the tool
that runs open-source LLMs (Llama, Gemma, Qwen, and others) directly
on your own machine instead of calling a cloud API. Do these in order,
top to bottom, each lesson folder has a `README.md` (read first) and a
`lesson.py` (run second). Don't move to the next lesson until the
current one's checkpoint questions feel solid.

This course assumes you've done the [langchain](../langchain/) course
through at least Lesson 11 (`init_chat_model`), where the model behind
an agent was already shown to be swappable. Every other course in this
repo calls Gemini over the network; this one builds the exact same
kinds of agents, generate calls, tool-calling loops, and RAG, against
a model running locally, with no API key and no per-token cost.

Setup: install Ollama itself first (this is a separate application,
not a Python package): [ollama.com/download](https://ollama.com/download),
then confirm it worked with `ollama --version`. Pull a small model to
start with:

```bash
ollama pull llama3.2
```

No `.env` entry is required for the local server (it runs on
`http://localhost:11434` by default), but the Python client is already
part of this project's dependencies via `uv sync`. Then, from the
project root:

```bash
uv run python lessons/ollama/<tier>/<NN>_<name>/lesson.py
```

## Beginner: running and calling a local model

| # | Lesson | Concept |
|---|--------|---------|
| 01 | [what_is_ollama](01_beginner/01_what_is_ollama/) | Local model runtime, why agents use it (cost, privacy, offline) |
| 02 | [installing_and_pulling_models](01_beginner/02_installing_and_pulling_models/) | `ollama pull`, the model library, size/quantization tags |
| 03 | [first_generate_call](01_beginner/03_first_generate_call/) | The Python `ollama` client, `generate()` |
| 04 | [chat_vs_generate](01_beginner/04_chat_vs_generate/) | `chat()` messages API vs raw completion |
| 05 | [streaming_responses](01_beginner/05_streaming_responses/) | Streaming tokens back as they're generated |
| 06 | [model_parameters](01_beginner/06_model_parameters/) | `temperature`, `top_p`, `num_ctx`, system prompts |
| 07 | [listing_and_managing_models](01_beginner/07_listing_and_managing_models/) | `ollama list`, `show`, `rm`, disk and memory footprint |
| 08 | [embeddings_with_ollama](01_beginner/08_embeddings_with_ollama/) | `embed()`, running an embedding model locally |
| 09 | [beginner_checkpoint_project](01_beginner/09_beginner_checkpoint_project/) | **Checkpoint:** a streaming chatbot with a system prompt, fully offline |

## Intermediate: structured output, tools, and swapping into existing agents

| # | Lesson | Concept |
|---|--------|---------|
| 10 | [structured_output](02_intermediate/10_structured_output/) | JSON-mode / schema-constrained output, validating with Pydantic |
| 11 | [tool_calling_with_ollama](02_intermediate/11_tool_calling_with_ollama/) | Function/tool calling support in local models |
| 12 | [multi_turn_memory](02_intermediate/12_multi_turn_memory/) | Keeping conversation history across turns |
| 13 | [swapping_into_langchain](02_intermediate/13_swapping_into_langchain/) | `ChatOllama` as a drop-in replacement for Gemini |
| 14 | [swapping_into_pydantic_ai](02_intermediate/14_swapping_into_pydantic_ai/) | Pointing a pydantic_ai agent at a local model |
| 15 | [comparing_models](02_intermediate/15_comparing_models/) | Running two local models side by side, quality/speed/size tradeoffs |
| 16 | [custom_models_with_modelfile](02_intermediate/16_custom_models_with_modelfile/) | `Modelfile`, baking a system prompt into a named model |
| 17 | [intermediate_checkpoint_project](02_intermediate/17_intermediate_checkpoint_project/) | **Checkpoint:** a tool-calling local agent, zero cloud calls |

## Advanced: production concerns for local inference

| # | Lesson | Concept |
|---|--------|---------|
| 18 | [gpu_vs_cpu_and_quantization](03_advanced/18_gpu_vs_cpu_and_quantization/) | Hardware tradeoffs, quantization levels (q4, q8, fp16) |
| 19 | [context_window_management](03_advanced/19_context_window_management/) | `num_ctx` limits, truncation strategies |
| 20 | [concurrent_requests](03_advanced/20_concurrent_requests/) | Serving multiple requests against one local model, queueing behavior |
| 21 | [local_rag_with_ollama](03_advanced/21_local_rag_with_ollama/) | Pairing local embeddings with local generation for RAG |
| 22 | [running_as_a_background_service](03_advanced/22_running_as_a_background_service/) | `ollama serve`, keeping it alive, ports |
| 23 | [security_and_network_exposure](03_advanced/23_security_and_network_exposure/) | Binding to localhost vs network, no built-in auth |
| 24 | [advanced_capstone_project](03_advanced/24_advanced_capstone_project/) | **Capstone:** a fully offline RAG agent, no API calls at all |
