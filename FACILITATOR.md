# Facilitator notes

## Before teaching

Ask students to complete [SETUP.md](SETUP.md), including the live Groq check, before class.
The class target is **35 minutes**. Confirm this with a timed pilot; API latency and student familiarity will affect the pace.

Run the exercise from a fresh GitHub clone on `main`, following only the README.
Check that students can distinguish a JSON tool request from an executed tool.
For weather, compare the final answer against the returned readings, units, timestamp, and source.

The default model is `openai/gpt-oss-20b` on Groq. Check [model access and limits](https://console.groq.com/docs/rate-limits) before class.
If you change the model, pilot it first and give students the exact `GROQ_MODEL` environment value.
Each student should use their own key. A weather round trip normally uses two model requests.

## Schedule

| Part | Minutes | Teaching focus |
| --- | ---: | --- |
| Start and bare model demo | 10 | Five minutes to settle in and check setup, then five to inspect a model call. |
| Protocol | 6 | The model produces a request; nothing executes yet. |
| Dispatcher | 6 | Python validates and executes an allowed tool. |
| Loop | 10 | The tool result enters the next model request. |
| Discussion | 3 | History and execution limits belong to the harness. |

Students make three commits, one after each implementation checkpoint.
The HTTP, parser, weather, and CLI code is supplied. Keep attention on the prompt and the four missing lines.
Use the README's prediction and explanation questions before moving on.

A bare model may honestly admit it lacks current data. The demo does not depend on it hallucinating.
Open-Meteo returns current weather estimates rather than guaranteed instantaneous station observations.

## When a student gets stuck

Use [SETUP troubleshooting](SETUP.md#troubleshooting). If live access fails, pair the student with someone whose setup works.
Offline tests prove application behavior with controlled responses; they do not prove hosted-model decisions or factual accuracy.
Do not spend the session repeatedly retrying a model that ignores the protocol.

The `tool_result` user message is our custom protocol, not the provider's native tool format.
Native tool calling is a closing comparison or later exercise. Keep extra tools and retries out of the core session.

## Reference code

In a GitHub clone, inspect the completed source without switching away from unfinished work:

```bash
git show origin/solution:workshop.py
```

For a separate runnable solution checkout, from the cloned repository:

```bash
git worktree add --detach ../agent-harness-workshop-solution origin/solution
cd ../agent-harness-workshop-solution
python -m unittest discover -s tests -v
python workshop.py --mode agent --prompt "What is the weather in Vancouver right now?"
```

Use the same terminal and active Python environment as setup so the key and interpreter remain available.
In the original local repository, replace `origin/solution` with `solution`.

The `short-0` through `short-3` tags preserve the starter, protocol, dispatcher, and loop reference code.
Use the current README for instructions; tagged documentation may describe an earlier presentation of the same exercise.
The old `checkpoint-*` tags and `archive/long-workshop` branch belong to the earlier long exercise.
Keep archive references out of the student path.

When publishing, include `main`, `solution`, and the four `short-*` tags. The local archive need not be published.
