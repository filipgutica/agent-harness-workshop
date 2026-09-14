# Facilitator notes

This version is a 35-minute activity for BCIT CST term 3 students. Students should know basic Python functions, dictionaries, JSON, HTTP, and Git.

## Before class

Ask students to complete [SETUP.md](SETUP.md) before the session. Python, Git, a Groq account, a Groq API key, and internet access are prerequisites. Do not use class time to install software or create accounts.

Pilot the completed `solution` branch with your own key. Try a direct answer, a Vancouver weather question, and a question about another location. Check that the trace shows a model action, a weather result, and a final response. Do not share your key with students. Model access and rate limits can change; check the [Groq quickstart](https://console.groq.com/docs/quickstart) and [rate limits](https://console.groq.com/docs/rate-limits) before class.

The default model is `openai/gpt-oss-20b`. Set `GROQ_MODEL` only if you need to use another model that your account can access. The program sends raw HTTP requests to `https://api.groq.com/openai/v1/chat/completions`.

The repository uses `main` as the student starting point and `solution` as the completed reference. `archive/long-workshop` preserves the earlier two-hour exercise. The `short-0` through `short-3` tags mark this version. The older `checkpoint-0` through `checkpoint-5` tags belong to the archived exercise.

## Schedule

| Part | Time | Student activity | Prompt to pause on |
| --- | ---: | --- | --- |
| Setup check | 5 min | Run the echo command and supplied-code tests. Read the TODOs. | What does the program know before it calls a model? |
| Bare model demo | 4 min | Ask one normal question and one current-weather question in `chat` mode. Predict what evidence each answer has. Create the empty baseline commit. | Can the model observe Vancouver right now? |
| Checkpoint 1: protocol | 7 min | Replace `SYSTEM_PROMPT`. Run the action mode and inspect the JSON. Commit. | Is a JSON request the same as running a tool? |
| Checkpoint 2: dispatcher | 5 min | Replace the dispatcher TODO line. Run the weather tests. Commit. | Who controls which Python function can run? |
| Checkpoint 3: loop | 10 min | Replace the three loop TODO lines. Run the full suite and one agent call. Commit. | What must the second model request contain? |
| Discussion | 4 min | Trace the two model calls and one tool call. | What would happen without `MAX_STEPS`? |

The target is 35 minutes; confirm the pace in a timed pilot before teaching. The baseline commit uses `git commit --allow-empty` after the bare model demo. Each of the three implementation checkpoints has one commit. Students should stage only `workshop.py`.

## Run the activity

Keep students in `workshop.py`. The helpers already implement the Groq request, action parser, Vancouver weather request, CLI, and loop structure. Students make three small changes:

1. Replace the full `SYSTEM_PROMPT` block from the README.
2. Replace the dispatcher TODO with `return tools[tool_name](location=parameters['location'])`.
3. Replace TODO 3a with `raw = call_model(messages)`, TODO 3b with `result = dispatch_tool(action)`, and TODO 3c with `messages.append({'role':'user','content':json.dumps(tool_result)})`.

Have students predict the output before each live command. Print the raw model text and tool result so they can see the harness work. The first action command validates the model response but does not execute a weather request. The agent command executes the allowlisted tool and sends its result in the next request.

If a student gets invalid JSON, ask them to inspect the raw `Model:` line and compare their prompt with the README. They can retry once. Live model output is not deterministic, and the protocol tests cannot prove that a hosted model follows the prompt.

If a student gets an HTTP error, check the current terminal's `GROQ_API_KEY`, `GROQ_MODEL`, internet access, and account limits. The [SETUP troubleshooting notes](SETUP.md#troubleshooting) give the same checks.

## Teaching points

A bare language model can generate a plausible answer from its training and the prompt. It has no fresh weather observation in this program. The application adds that capability by calling Open-Meteo.

The model returns a JSON value as text. `parse_action` validates that value. `dispatch_tool` checks the tool allowlist and parameter shape before Python calls `get_weather`. A tool name from the model is data until the application accepts and dispatches it.

The second request includes the original conversation, the assistant's tool-call JSON, and a user message containing `tool_result`. The model uses the returned values, units, time, and source to write the final answer. The tool result is a user-role message by teaching choice; provider-native tool calling uses dedicated fields but keeps the same application-controlled loop.

`MAX_STEPS = 5` prevents repeated tool calls from running forever. The code stops on malformed model output, a rejected tool request, or a tool error. Retries, multiple tools, and persistent chat history are possible follow-up exercises.

Open-Meteo returns current modelled conditions. If students publish output, ask them to credit Open-Meteo under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Reference commands

To inspect the reference code without changing a student's branch:

```bash
git show solution:workshop.py
```

To run a separate reference checkout from the repository root:

```bash
git worktree add --detach ../agent-harness-workshop-solution solution
cd ../agent-harness-workshop-solution
python -m unittest discover -s tests -v
python workshop.py --mode agent --prompt "What is the weather in Vancouver right now?"
```

The key must be set in the terminal that runs the reference. On Windows, use `py -3` in place of `python`.

Keep the tags stable while students use the repository. If you change the starter or solution, update the affected checks and tags before the next cohort.
