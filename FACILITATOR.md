# Facilitator notes

## Before class

Have students complete [SETUP.md](SETUP.md), including the live Groq check.
Keep that terminal open; it holds their API key.
The audience is BCIT CST term 4. Students need basic functions, dictionaries, conditionals, and loops.
Do not assume Git experience. Students can complete the coding lesson without commits.

Rehearse the README from a fresh starter copy. **40 minutes is a target, not a measured completion time.**
Keep your completed reference copy separate from the student starter.
Students edit `workshop.py`; the supplied helpers handle HTTP, validation, and terminal input.

## Start at the whiteboard

Write this sequence:

```text
Question -> model requests a tool -> harness runs it -> result -> model answers
```

Ask: "Which part executes the function?" The harness does.
The model generates a request; it does not execute the local function.

Introduce only the roles needed for the first request: `system` instructions, `user` question, `assistant` reply.
Introduce `tool` when returning the result in step 3.
Use the README glossary when a term needs explanation.

## Teaching sequence

| Part | Minutes | What students should see |
| --- | ---: | --- |
| 0. Starter | 4 | A greeting answer; no current weather data. |
| 1. Native tool request | 6 | An assistant message containing `tool_calls`. No function has run yet. |
| 2. Execute the tool | 7 | Weather data returned by the harness. No follow-up model call yet. |
| 3. Return the result | 10 | A second model call turns the data into a weather answer. |
| 4. Format the answer | 10 | A separate request produces `{"answer": "..."}`; invalid formatting is retried. |
| 5. Discussion | 3 | Students explain who requests, executes, and answers. |

Before each edit, have students type `/exit`. Then edit, save, and restart.
Use **What is the temperature in Vancouver right now?** through all stages so the changed behavior is easy to compare.
Use **hello** to show the path that needs no tool.
Pause at each README **Check** before moving on.

Imports are introduced when used: transport/CLI in step 1, dispatch/logging in step 2, answer validation in step 4.
When a student gets stuck, compare the complete imports, constants, function, and CLI block with that stage.
Keep one CLI entry point at the bottom. Constants and functions belong at the left edge, not inside another function.
An old file using `parse_action` needs all step 1 replacements; changing that import alone is insufficient.

## Explain the native tool loop

In step 1, `TOOLS` describes a callable function and its arguments. The system prompt explains when to request it.
An argument schema does not execute the function or format the final answer.
`call_model` returns an assistant message dictionary. A tool request can have `content: None`.

In step 2, `dispatch_tool` checks the function name, parses arguments, and runs only the allowed function.
`get_weather` makes two GET requests: Open-Meteo geocoding for coordinates, then a forecast request.
These are work inside one agent iteration, not two model calls.
The first matching city is used. Ask students to check the resolved location; try Tokyo after Vancouver.
[Open-Meteo's current weather is a model estimate](https://open-meteo.com/en/docs#current).

In step 3, show these adjacent messages in the trace:

```text
[ASSISTANT_MESSAGE] with tool_calls[].id
[TOOL_MESSAGE] with the same tool_call_id
```

Both must stay in history. A reply can request multiple calls; each ID needs a result before the next model request.
Appending to `messages` changes a local list. The next HTTP request sends the entire updated list.
Tool data is supplied by the harness, so it uses the `tool` role.

**One agent iteration means one model call in that loop.**
A greeting usually takes one; weather usually takes two.
`MAX_STEPS = 5` is an upper bound, not five required steps or five JSON parsing attempts.
API and tool failures end the question immediately.
Each new CLI question starts fresh; a missing-city clarification must be followed by the full question with its city.

`Output:` is what the student's function returns, printed by `run_cli`.
Step 2 returns data. Step 3 returns model-written answer text.
There is no hidden model call after `Output:`.

## Keep formatting separate

Step 3 already completes native tool calling. Step 4 adds a new request to format the finished answer.
`format_answer` has no tools. `parse_answer` requires exactly one nonempty string field named `answer`.
Correction feedback uses the `user` role because it is feedback, not a tool result.

`MAX_RETRIES = 2` allows one initial formatting request and two corrections.
Only invalid formatting is retried; API failures propagate.
A successful weather question usually takes three model calls at this stage: request, answer, format.
The maximum is eight calls: five in the tool loop plus three in formatting.
Check the formatted facts against the tool data; valid JSON does not prove factual accuracy.

For a predictable retry demonstration after step 4:

```bash
python -m unittest tests.test_limits.HarnessSafetyTests.test_format_answer_stops_after_the_maximum_number_of_retries -v
```

The fake reply is deliberately invalid. `OK` means the test confirmed the stopping bound.
On Windows, use `.\.venv\Scripts\python.exe` instead of `python` in these commands.

## Verify the lesson

Setup checks **15 tests**. After step 4, run all **30 tests**:

```bash
python -m unittest discover -s tests -v
```

Tests use fake replies. They verify harness behavior, not live provider behavior or weather accuracy.
Rehearse a greeting, a weather question, and optional output modes with live requests separately.
Check [model access](https://console.groq.com/docs/models) and [rate limits](https://console.groq.com/docs/rate-limits).
The default is `openai/gpt-oss-120b`; rehearse all stages if you change it.
Each student uses their own key. For access failures, use [SETUP troubleshooting](SETUP.md#troubleshooting) or pair students.

The Git checkpoint in step 4 is optional. Saving makes code runnable; committing records a checkpoint.
Let students finish the lesson before spending time on Git identity or commit errors.

## Optional strict schema lesson

[README step 6](README.md#6-optional-enforce-a-json-schema) is outside the core schedule.
Compare prompt-only JSON, JSON mode, and a strict schema.
[Groq Structured Outputs](https://console.groq.com/docs/structured-outputs) currently cannot be combined with tools; apply it to the separate formatter.
The strict version removes the correction loop and `MAX_RETRIES`.
It guarantees the supported schema for successful, complete replies, not correct facts.
Keep local validation and API/truncation handling. The example schema allows an empty string; the local validator rejects it.

The retry tests no longer apply after that replacement. Use the README's **24 unchanged helper and agent checks**, then rehearse strict output live.

## Prepare an instructor reference

Use current `main` with its compatible helpers. Create a separate reference copy:

```bash
git worktree add --detach ../agent-harness-workshop-reference main
```

```bash
cd ../agent-harness-workshop-reference
```

Follow README steps 1–4, then run the full suite and a live weather question.
The historical `solution` branch uses an older custom text protocol; use the current README for this native-tool lesson.
