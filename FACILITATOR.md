# Facilitator notes

## Before teaching

Ask students to complete [SETUP.md](SETUP.md), including its live Groq check, before class.
Pilot the README from a fresh clone. The target is **35 minutes**, not a measured completion time.
Students need basic functions, dictionaries, conditionals, loops, and Git.

The starter is 15 lines. It runs immediately and has no TODO exceptions.
Students edit only `workshop.py`; `helpers.py` contains the existing HTTP requests, validation, and terminal handling.
Explain that moving HTTP code into another file does not make it an agent framework.
The model still receives raw chat-completion requests.

## Schedule

| Part | Minutes | Teaching focus |
| --- | ---: | --- |
| Starter | 5 | Input, two messages, a model call, output. |
| JSON prompt | 7 | A tool request is still just text. |
| Tool execution | 8 | Python validates the request and fetches weather. |
| Agent loop | 12 | Add both the model request and tool result to history. |
| Discussion | 3 | Explain what the harness owns. |

Each of the three edits leaves a runnable program. Students commit after each successful stage.
They replace complete blocks instead of filling scattered blanks.
Keep the same command, `python workshop.py`, throughout.

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
Open-Meteo returns current estimates rather than guaranteed instantaneous station observations.

Check Groq model access and [rate limits](https://console.groq.com/docs/rate-limits) before class.
The default is `openai/gpt-oss-20b`. If you change `GROQ_MODEL`, pilot the replacement first.
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
Older `short-*` tags and the local `archive/long-workshop` branch preserve previous versions.
They are historical references, not steps in the current exercise. Do not direct students to them.
