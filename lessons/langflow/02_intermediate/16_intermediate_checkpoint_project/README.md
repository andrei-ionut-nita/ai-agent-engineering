# Lesson 16: Checkpoint. An Agent, a custom tool, called over REST

## What we're building

Every piece from Intermediate, in one flow: an Agent (Lesson 14)
connected to a real Gemini model, given both a Custom Component tool
(Lesson 12-13's `WordLengthTool`) and a built-in tool
(`add_calculator_tool`), its API key coming from a Global Variable
(Beginner Lesson 7), the whole thing uploaded and run over the REST API
(Lesson 11), not `run_flow_from_json`.

## Do this yourself

1. Build the flow fresh, from an empty canvas:
   - **Chat Input**.
   - **Google Generative AI**, model `gemini-3.5-flash-lite`, API key
     picked from the `GOOGLE_API_KEY` Global Variable.
   - A **New Custom Component**, code pasted in from `WordLengthTool`
     in `lesson.py` (Lesson 13's tool, exactly).
   - **Agent**, **Calculator** toggle on, `Model` connected from Google
     Generative AI's model output, `Tools` connected from Word Length's
     tool output.
   - **Chat Output**.
2. Wire it exactly like Lesson 13's flow, plus the Calculator toggle
   from Lesson 14.

   No `canvas.png` ships with this lesson, the same reason as Lesson
   13: re-importing a saved flow that wires a model into an Agent's
   Model field trips a frontend re-import quirk in this Langflow
   version (the edge gets silently dropped with an "invalid
   connections" notice, even though the flow runs correctly). Build it
   by hand following the steps above and the wiring holds.

3. Upload the flow and run it over the REST API (or just use the
   Playground, same underlying call), ask it something that needs the
   custom tool ("how many letters in 'checkpoint'?") and something that
   needs the built-in one ("what's 12 times 12?"). Confirm both come
   back correct, that's proof the Agent is picking the right tool for
   each question, not just always answering from what the model already
   knows.

## Running it

```bash
uv run python lessons/langflow/02_intermediate/16_intermediate_checkpoint_project/lesson.py
```

## Expected output

Approximate for the first answer, exact for the second:

```
> How many letters are in the word 'checkpoint'?
There are 10 letters in the word 'checkpoint'.

> What is 12 times 12?
12 times 12 is 144.
```

## Try this yourself

- Add a second Custom Component tool of your own (a Fahrenheit-to-Celsius
  converter is a good small one) and confirm the Agent picks it
  correctly when asked a question that needs it.
- Swap `add_calculator_tool` off and ask the same arithmetic question
  again, confirm Gemini still attempts an answer on its own, without a
  tool, and think about when you'd actually want that fallback versus
  forcing tool use.
- Remove the Global Variable and hardcode the API key instead (Lesson
  7's exercise, repeated here in a bigger flow), confirm it still runs,
  then put the Global Variable back.

If you can make these changes confidently, you're ready for the
Advanced tier, starting at Lesson 17.
