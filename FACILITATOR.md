# Facilitator notes

## Before teaching

Ask students to complete [SETUP.md](SETUP.md), including its live Groq check, before class.
Pilot the README from a fresh clone. The target is **40 minutes**, not a measured completion time.
The audience is **BCIT CST term 4**. Students need basic functions, dictionaries, conditionals, loops, and Git.

The starter is a small, runnable model call with comments and no TODO exceptions.
Students edit only `workshop.py`; `helpers.py` contains the existing HTTP requests, validation, and terminal handling.
Explain that moving HTTP code into another file does not make it an agent framework.
The model still receives raw chat-completion requests.

Before presenting:

- Keep a starter copy for the live edits and a separate solution copy for reference.
- Use a large editor font and terminal font so students can read the code and output.
- Check the live weather prompt and a direct-answer prompt with your own key.
- Confirm students have their `my-workshop` branch, 10 passing setup tests, and a live reply.
- Keep the setup terminal open. A new terminal needs its environment and key set again.

## Schedule

| Part | Minutes | Teaching focus | Check before moving on |
| --- | ---: | --- | --- |
| Starter | 4 | Input, two messages, a model call, output. | Students can find the model call. |
| JSON prompt | 6 | A tool request is still just text. | Output contains a JSON `tool-call`. |
| Tool execution | 7 | Python validates the request and fetches weather. | Output contains weather data. |
| Agent loop | 10 | Add both the model request and tool result to history. | Weather data is followed by a final answer. |
| Formatting retries | 10 | Send validation feedback, with two correction attempts per action. | Students can distinguish both limits; 22 tests pass. |
| Discussion | 3 | Explain what the harness owns. | Students can explain who executes the tool. |

Each of the four edits leaves a runnable program. Students commit after each successful stage.
They replace complete blocks instead of filling scattered blanks.
Keep the same command, `python workshop.py`, throughout.

Use **What is the temperature in Vancouver right now?** at every stage.
Before each run, ask students to predict the output. Pause for them to save, run, and compare it with the README.
After step 3, use **What is a Python dictionary?** to show that a direct answer skips the tool.

Point to these boundaries as you teach:

- `call_model` sends messages and returns text. It does not execute tools.
- `parse_action` converts that text into a dictionary and checks its shape.
- `dispatch_tool` allows only registered functions with valid arguments.
- `request_action` records model replies, validates actions, and asks for bounded formatting corrections.
- `run_agent` adds tool results to history and controls the tool loop.

The tool-execution stage intentionally prints raw weather JSON. It does not send that data back to the model yet.
Step 3 adds the loop and produces a model-written answer. Step 4 adds bounded formatting retries.
Use that difference to explain why a tool call and an agent loop are separate concepts.

## Verification and troubleshooting

The setup suite runs 10 tests against the supplied helpers and CLI.
Run the complete 22-test suite only after step 4:

```bash
python -m unittest discover -s tests -v
```

The agent tests describe the final behavior and will fail on the starter or intermediate stages.
All tests are offline. They cannot prove that a hosted model follows the prompt or uses readings accurately.
Compare the live final answer with the tool's readings, units, timestamp, and source.
[Open-Meteo returns weather model estimates](https://open-meteo.com/en/docs#current), so describe the data as estimates.

Check Groq model access and [rate limits](https://console.groq.com/docs/rate-limits) before class.
The default is [`openai/gpt-oss-20b`](https://console.groq.com/docs/models). If you change `GROQ_MODEL`, pilot the replacement first.
A successful weather interaction normally uses two model requests when no formatting retry is needed. Each student should use their own key.
If access fails, use [setup troubleshooting](SETUP.md#troubleshooting) and pair the student with someone whose setup works.

An honest admission of uncertainty is a valid starter result; the lesson does not depend on hallucination.
Native tool calling, additional tools, and retries for network or service failures belong in a later exercise.

For the retry demonstration, use the offline suite's deliberately invalid replies.
Students should see `Retry 1/2:` and `Retry 2/2:` before the format-exhaustion test stops.
Explain that `MAX_RETRIES = 2` means three attempts per action and `MAX_STEPS = 5` means five valid actions.
The maximum is 15 model requests per question. API and tool failures do not enter the formatting retry path.

## Optional schema extension

[README step 6](README.md#6-optional-enforce-a-json-schema) is for extra time or after class, outside the 40-minute core schedule.
It compares JSON mode with strict schema enforcement on the same chat-completions endpoint.
Students still edit only `workshop.py`; `call_model` accepts the optional `response_format` keyword argument.

Pilot both bonus modes with the default model before demonstrating them.
Keep the JSON instructions in the prompt when enabling JSON mode.
For strict mode, point out that all fields are required and unused fields contain `null`.
The bonus `request_action` removes those unused fields before applying the original action validator.

Ask students which rules the schema enforces and which Python still enforces.
The schema controls structure; Python checks the requested tool, arguments, and loop limit.
The API does not run the weather tool merely because a response matches the schema.
This is a production technique for response formatting, while native tool calling remains a separate API interface.
See [Groq's schema requirements](https://console.groq.com/docs/structured-outputs) before changing the example.

The offline suite contains 22 tests and works after either bonus mode.
Its fake replies do not prove live schema enforcement. Compare the live `Model:` output with the supplied schema.
Apply the bonus after the retry step on the student's branch from `main`.

## Branches and the reference solution

GitHub has the starter branch `main` and the original loop reference `solution`, which covers README steps 1–3.
The current retry version is the complete block in README step 4; the remote reference branch has not been updated with that extension.
`origin/solution` is Git's reference to the GitHub branch; it is not a second solution.

From a clone, read the original tool loop without replacing student work:

```bash
git show origin/solution:workshop.py
```

To run it in a separate directory:

```bash
git worktree add --detach ../agent-harness-workshop-solution origin/solution
cd ../agent-harness-workshop-solution
python -m unittest discover -s tests -v
python workshop.py
```

Keep the setup terminal open so its Python environment and Groq key remain available.
