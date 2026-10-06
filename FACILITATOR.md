# Facilitator notes

## Before teaching

Ask students to complete [SETUP.md](SETUP.md), including its live Groq check, before class.
Pilot the README from a fresh clone. The target is **40 minutes**, not a measured completion time.
The audience is **BCIT CST term 4**. Students need basic functions, dictionaries, conditionals, and loops.
The instructions introduce the Git commands; do not assume students know branches, staging, or commits.

### Audience and learning goals

The [BCIT CST curriculum](https://www.bcit.ca/programs/computer-systems-technology-diploma-full-time-5500dipma/#courses)
places procedural and object-oriented programming before term 4. Internet Software Architecture (COMP 4537), including HTTP and REST, is in term 4.
Use that background to connect the harness to familiar ideas: input validation, function dispatch, state, and exception handling.
Students may still be taking the API course and have different specializations. Introduce the model's message protocol explicitly.

By the end, students should trace a native tool request to an allowed function, link its result by ID, and explain the model's next request.
They should distinguish the tool loop from a separate answer-formatting retry loop.
Students edit only `workshop.py`; supplied helpers own HTTP, validation, and CLI handling.

Before presenting:

- Keep starter and completed copies in separate directories.
- Pilot every README stage, including native weather requests and both optional output modes.
- Confirm students have their branch, 15 passing setup tests, and a live greeting.
- Ask students to run `git status` and find `On branch my-workshop` before editing.
- Keep the setup terminal open so its environment and API key remain available.

## Schedule

| Part | Minutes | Teaching focus | Check before moving on |
| --- | ---: | --- | --- |
| Starter | 4 | System prompt, user question, assistant content. | Students find the model request. |
| Native tool request | 6 | `tools` declaration and assistant `tool_calls`. | A weather request contains an ID and JSON argument text. |
| Tool execution | 7 | Validate arguments and dispatch an allowed function. | Output shows weather data. |
| Agent loop | 10 | Assistant request plus matching `tool` messages. | The next model call produces a weather answer. |
| Formatting retries | 10 | Prompt-only JSON, local validation, bounded corrections. | Students distinguish both budgets; 30 tests pass. |
| Discussion | 3 | Explain what the harness owns. | Students identify who executes tools. |

Each edit leaves a runnable program. Use **What is the temperature in Vancouver right now?** at every stage.
Distinguish editor saves from Git commits: saves update the runnable file; commits record checkpoints.
The step 4 checkpoint is optional. Let students finish the harness exercise before helping with Git identity or commit errors.
Ask students to predict output before running it. After step 3, try Tokyo and a direct-answer question.
A weather tool call makes two GET requests: geocoding and forecast. They are not separate agent loop iterations.
Use the resolved city to discuss ambiguous names and the first-match geocoding policy.
[Open-Meteo's current weather is a model estimate](https://open-meteo.com/en/docs#current).

## Explain the boundaries

- `call_model` returns an assistant message dictionary, not just its text. It preserves native `tool_calls` and strips server metadata.
- `dispatch_tool` decodes argument JSON, validates the function and arguments, and executes the allowlisted function.
- `run_agent` records assistant replies and matching `tool` results, resends history, and enforces `MAX_STEPS`.
- `parse_answer` checks the final JSON answer's syntax, fields, and nonempty string.
- `format_answer` handles formatting separately; `answer_question` connects the phases.

The model requests a tool but cannot execute the local function itself.
The tool declaration's argument schema and final-answer schema have different purposes.
The former describes a callable interface; the latter constrains the answer's structure.
Local argument validation is still required before dispatch.

Read the message trace with students:

```text
[SYSTEM_PROMPT] + [USER_MESSAGE] + [ASSISTANT_MESSAGE] + [TOOL_MESSAGE]
```

Show the assistant's `tool_calls[].id` and the matching `tool_call_id` on its result.
Tool data comes from the harness. It is not a user message.
Appending changes local history; the next HTTP request sends that history to the model.
`Model reply (raw):` shows the assistant message before student processing, with server metadata omitted.
`Output:` is the function's return value printed by the CLI, not another actor or implicit model request.
Step 2 returns tool data; step 3 returns model-written text; step 4 explicitly adds a formatting request.

## Verify and rehearse

Setup runs 15 offline helper/CLI tests. Run all 30 tests only after README step 4:

```bash
python -m unittest discover -s tests -v
```

Tests use fake responses. They prove protocol handling and limits, not live model behavior or factual accuracy.
Compare live weather answers with the tool data, including location, units, timestamp, timezone, and source.
Check [model access](https://console.groq.com/docs/models) and [rate limits](https://console.groq.com/docs/rate-limits) before class.
A greeting alone does not verify native tool calling or strict output support. Rehearse those requests separately.
The default model is `openai/gpt-oss-120b`; pilot all stages if you override it.
Each student uses their own key. For access failures, use [SETUP troubleshooting](SETUP.md#troubleshooting) or pair students.

For an offline correction-loop demonstration after step 4:

```bash
python -m unittest tests.test_limits.HarnessSafetyTests.test_format_answer_stops_after_the_maximum_number_of_retries -v
```

The deliberately invalid reply exhausts the budget; the test catches the error.
`MAX_RETRIES = 2` means three formatting attempts after the tool loop.
`MAX_STEPS = 5` means at most five requests within the tool loop.
A direct answer ends the loop after one iteration; weather normally takes two.
Step 4 adds one formatting call on success. The maximum is eight model requests per question.
API and tool failures never enter the format-correction loop.

## Optional schema extension

[README step 6](README.md#6-optional-enforce-a-json-schema) is outside the 40-minute core schedule.
Present it as a way to replace increasingly complex prompt-only formatting and correction logic.
JSON mode guarantees syntax; strict Structured Outputs guarantees a supported schema for successful, complete replies.
Supplying a schema with `strict: false` gives best-effort adherence.
[Groq currently cannot combine Structured Outputs with tool use](https://console.groq.com/docs/structured-outputs), so use the separate formatting request.
The strict example removes the correction loop and `MAX_RETRIES`; retain parsing, application validation, and API/truncation handling.
The example schema permits an empty string, while the local validator rejects it. Schema adherence alone does not prove facts.

Step 4's formatter-retry tests no longer describe the strict formatter. The README gives the 24 unchanged helper/native-agent checks to run instead.
Then rehearse the strict request live; mock tests cannot establish the provider guarantee.

## Prepare an instructor copy

Use current `main` for a starter with compatible helpers. Create a separate reference worktree:

```bash
git worktree add --detach ../agent-harness-workshop-reference main
```

```bash
cd ../agent-harness-workshop-reference
```

Follow README steps 1–4 in order, then run the complete offline suite and a live weather question.
The historical `solution` branch uses the older custom text protocol; it is not the solution for this native-tool workshop.
