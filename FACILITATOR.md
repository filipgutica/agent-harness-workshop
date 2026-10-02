# Facilitator notes

## Before teaching

Ask students to complete [SETUP.md](SETUP.md), including its live Groq check, before class.
Pilot the README from a fresh clone. The target is **35 minutes**, not a measured completion time.
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
| Starter | 5 | Input, two messages, a model call, output. | Students can find the model call. |
| JSON prompt | 7 | A tool request is still just text. | Output contains a JSON `tool-call`. |
| Tool execution | 8 | Python validates the request and fetches weather. | Output contains weather data. |
| Agent loop | 12 | Add both the model request and tool result to history. | Weather data is followed by a final answer; 20 tests pass. |
| Discussion | 3 | Explain what the harness owns. | Students can explain who executes the tool. |

Each of the three edits leaves a runnable program. Students commit after each successful stage.
They replace complete blocks instead of filling scattered blanks.
Keep the same command, `python workshop.py`, throughout.

Use **What is the temperature in Vancouver right now?** at every stage.
Before each run, ask students to predict the output. Pause for them to save, run, and compare it with the README.
After step 3, use **What is a Python dictionary?** to show that a direct answer skips the tool.

Point to these boundaries as you teach:

- `call_model` sends messages and returns text. It does not execute tools.
- `parse_action` converts that text into a dictionary and checks its shape.
- `dispatch_tool` allows only registered functions with valid arguments.
- `run_agent` adds the results to history and controls the loop.

The tool-execution stage intentionally prints raw weather JSON. It does not send that data back to the model yet.
The last stage adds the loop and produces a model-written answer.
Use that difference to explain why a tool call and an agent loop are separate concepts.

## Verification and troubleshooting

The setup suite runs 10 tests against the supplied helpers and CLI.
Run the complete 20-test suite only after the final stage:

```bash
python -m unittest discover -s tests -v
```

The agent tests describe the final behavior and will fail on the starter or intermediate stages.
All tests are offline. They cannot prove that a hosted model follows the prompt or uses readings accurately.
Compare the live final answer with the tool's readings, units, timestamp, and source.
[Open-Meteo returns weather model estimates](https://open-meteo.com/en/docs#current), so describe the data as estimates.

Check Groq model access and [rate limits](https://console.groq.com/docs/rate-limits) before class.
The default is [`openai/gpt-oss-20b`](https://console.groq.com/docs/models). If you change `GROQ_MODEL`, pilot the replacement first.
A successful weather interaction normally uses two model requests. Each student should use their own key.
If access fails, use [setup troubleshooting](SETUP.md#troubleshooting) and pair the student with someone whose setup works.

An honest admission of uncertainty is a valid starter result; the lesson does not depend on hallucination.
Native tool calling, additional tools, and retries belong in a later exercise.

## Branches and the reference solution

GitHub has one starter branch, `main`, and one completed branch, `solution`.
`origin/solution` is Git's reference to the GitHub branch; it is not a second solution.

From a clone, read the completed source without replacing student work:

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
