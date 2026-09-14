# Facilitator notes

## Pilot the workshop

Use the README from `main` and create your own exercise branch. Follow every checkpoint and make its commit.
The supplied tests are offline. Passing them verifies application behavior under controlled responses,
not whether a particular hosted model will follow the prompt reliably.

Before class, run the completed solution with your own key. Try a normal question, Vancouver weather,
and an unsupported location. Check the printed weather values against the final answer.
Choose a fixed available free model if the `openrouter/free` router gives inconsistent results.
Share that exact model ID with the class using the `OPENROUTER_MODEL` environment variable.
Do not share a personal API key. Arrange account setup before the session.

To inspect the solution while preserving a student's work, use `git show` as described in the README.
For a separate runnable solution copy, use a worktree from the repository root:

```bash
git worktree add --detach ../agent-harness-workshop-solution solution
cd ../agent-harness-workshop-solution
python3 -m unittest discover -s tests -v
python3 workshop.py --mode agent --prompt "What is the weather in Vancouver right now?"
```

On Windows, use `py -3` instead of `python3` in these commands.
The key must be set in the terminal running the solution.
The worktree command creates a separate directory; it does not move the exercise checkout.

## Timing and teaching prompts

| Checkpoint | Minutes | Pause and ask |
| --- | --- | --- |
| 0: setup | 5 | What does this program currently know? |
| 1: raw API | 20 | What evidence supports the model's current-temperature answer? |
| 2: protocol | 20 | Is a JSON tool request already an executed tool? |
| 3: tool | 20 | Who controls which functions can run? |
| 4: history and loop | 20 | What information reaches the second model request? |
| 5: bounds and failures | 15 | How would an unbounded loop fail? |
| Discussion and buffer | 20 | What does an agent framework automate here? |

Describe a bare model as lacking fresh information and external execution capabilities.
Do not require it to hallucinate in the first demo. An honest admission of uncertainty demonstrates the same limitation.

Keep students focused on `workshop.py`. HTTP boilerplate can be completed together during checkpoint 1.
For students unfamiliar with `urllib`, show how a `Request`, a context manager, and JSON decoding fit together.
There are no packages to install. This keeps setup small, but basic Python syntax still needs a short introduction if unfamiliar.

## Reference checkpoints

The tags refer to supplied reference commits, not commits created by students.

| Tag | Reference behavior |
| --- | --- |
| `checkpoint-0` | CLI echoes input; unfinished functions raise clear TODO errors. |
| `checkpoint-1` | Plain model calls and HTTP error handling. |
| `checkpoint-2` | Prompt and JSON action validation. |
| `checkpoint-3` | Vancouver weather and explicit tool dispatch. |
| `checkpoint-4` | Two model calls permit one tool round trip. |
| `checkpoint-5` | Five-call budget permits repeated tool requests and stops at exhaustion. |

Native tool calling is a useful closing comparison. Our user-role `tool_result` envelope is a teaching convention.
Provider-native tools use dedicated fields and identifiers to associate requests with results.
Both approaches still require application code to validate and execute local tools.

This is a single-prompt CLI, not a persistent chat session. History lasts for one invocation.
It deliberately stops on malformed output or tool failure. Recovery and retries are extension exercises.

## Maintenance and publication

The repository starts local, with no remote configured. `main` is the student entry point.
If you later publish it, include both branches and the checkpoint tags so the reference commands work.
Do not merge the completed solution into `main`.

Keep setup and instruction corrections consistent across both branches.
If you change reference code, verify the affected checkpoint commands and update tags deliberately before the next cohort.
Avoid changing tags during an active workshop, when students rely on stable references.
