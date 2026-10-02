# Setup before class

You need **Python 3.10+**, **Git**, a **Groq API key**, and internet access.
There are no Python packages to install. Complete these steps before class;
account creation and software installation are outside the 40-minute exercise.
If you need them, install [Python](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads/) before starting.

## 1. Clone the repo and create your branch

Open a terminal in a directory where you keep projects. Run one code block at a time, in order.

Clone the starter:

```bash
git clone --branch main https://github.com/filipgutica/agent-harness-workshop.git
```

Move into the repo folder:

```bash
cd agent-harness-workshop
```

Create your branch:

```bash
git switch -c my-workshop
```

`main` is the starter. `my-workshop` is your local branch for the exercise; you do not need to push it to GitHub.
Open the `agent-harness-workshop` folder in your editor. Keep this terminal open, in that folder, for the remaining steps.
If you already have a copy with edits, use a separate directory for a fresh clone.

## 2. Prepare Python

Use the commands for your operating system. Run one code block at a time, in order.

### macOS / Linux

Check that Python is version 3.10 or newer:

```bash
python3 --version
```

Check that Git is installed:

```bash
git --version
```

Create the virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

### Windows PowerShell

Check that Python is version 3.10 or newer:

```powershell
py -3 --version
```

Check that Git is installed:

```powershell
git --version
```

Create the virtual environment:

```powershell
py -3 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If activation is blocked, use `.\.venv\Scripts\python.exe` instead of `python` in every later command.
You do not need to change the execution policy.

The virtual environment keeps this workshop's Python session separate from other projects.

Check the supplied code before adding your key:

```bash
python -m unittest tests.test_cli tests.test_model tests.test_protocol -q
```

Expect **10 tests, OK**. These checks run offline and do not need an API key.
The full test suite is for the completed exercise, so do not run it yet.

## 3. Set your Groq key

Sign in to [Groq Console](https://console.groq.com/keys) and create your own API key.
Enter it through the hidden prompt below. Do not paste it into source files or commits.

### macOS / Linux

Stay in your current shell. This command works in both Bash and Zsh.
Paste your key when asked, then press Enter.
The terminal will not display the key as you type or paste it.

```bash
export GROQ_API_KEY="$(python -c 'import getpass; print(getpass.getpass("Groq API key: "))')"
```

This uses Python's standard-library hidden prompt and makes the key available to the workshop.

### Windows PowerShell

Run one code block at a time. Enter your key through the hidden prompt:

```powershell
$secret = Read-Host "Groq API key" -AsSecureString
```

Make the key available to Python:

```powershell
$env:GROQ_API_KEY = [System.Net.NetworkCredential]::new('', $secret).Password
```

Remove the temporary variable:

```powershell
Remove-Variable secret
```

The key lasts for this terminal session. The application does not load `.env` files.
The supplied model is [`openai/gpt-oss-20b` on Groq](https://console.groq.com/docs/models); no model setting is required.

## 4. Check setup

```bash
python workshop.py --prompt "Reply with: ready"
```

This command makes one live model request. Expect `Assistant:` followed by a short reply without an error.
The wording can vary. Resolve any error before class.

You are ready when you have your own branch, passing offline checks, and a successful live reply.
During class, use this terminal to run the program; an editor's Run button may not have your API key.

**Next: [start the workshop](README.md#0-try-the-starter--4-minutes).**

## Troubleshooting

| Problem | What to do |
| --- | --- |
| Missing `GROQ_API_KEY` | Repeat step 3 in the same terminal that runs Python. |
| HTTP 401 | Check that you entered a valid Groq key. |
| HTTP 403 or unavailable model | Check your account's model access in Groq Console. |
| HTTP 429 | Pause live calls and check [Groq limits](https://console.groq.com/docs/rate-limits). Offline tests still work. |
| Invalid JSON before workshop step 4 | Copy the full system prompt again, then rerun once. Ask the instructor if it still fails. |
| Formatting retries are exhausted after workshop step 4 | Check the prompt and both functions against the complete README step 4 block. Do not keep increasing the retry limit. |
| A step does not behave as described | Compare the entire `run_agent` function with that step's code block. |
| Indentation error | Copy the whole function block, including its spaces. Do not use tabs. |
| `my-workshop` branch already exists | Run `git switch my-workshop` to resume. |
| Python cannot find `workshop.py` or `tests` | Run the command from the `agent-harness-workshop` folder. |
| A new terminal cannot find `python` or your key | Activate `.venv` and repeat step 3 in that terminal. |
| Git opens a pager | Press `q` to return to the terminal. |
| Network or certificate error | Check connectivity and your Python installation. Do not disable TLS verification. |

If Git asks for your identity, run each command with your own details, then retry the commit.

Set your name:

```bash
git config user.name "Your Name"
```

Set your email:

```bash
git config user.email "you@example.com"
```

[Groq API documentation](https://console.groq.com/docs/quickstart) · [Open-Meteo documentation](https://open-meteo.com/en/docs)

Weather data by [Open-Meteo](https://open-meteo.com/), licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Retain attribution when sharing weather output.
