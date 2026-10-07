# Setup before class

You need **Python 3.10+**, **Git**, a **Groq API key**, and internet access.
There are no Python packages to install. Complete these steps before class;
account creation and software installation are outside the 30-minute exercise.
If you need them, install [Python](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads/) before starting.

## 1. Get your own workshop copy

Use Terminal on macOS/Linux or PowerShell on Windows.
Open it in a folder where you keep projects. Run one code block at a time, in order.
Copy only the commands inside each block. Press Enter and wait for the command to finish before continuing.

Three Git terms used here:

| Term | Meaning |
| --- | --- |
| Repository (repo) | The project files and their recorded history. |
| Branch | A named line of history. You will work on a branch called `my-workshop`. |
| Commit | A checkpoint of selected changes, recorded locally by Git. |

Check that Git is installed:

```bash
git --version
```

Expect `git version` followed by a version number. If Git is missing, install it before continuing.
The `git switch` command below requires Git 2.23 or newer.

Download the starter and its history from GitHub. This creates a new folder called `agent-harness-workshop`:

```bash
git clone --branch main https://github.com/filipgutica/agent-harness-workshop.git
```

Move this terminal into that folder. `cd` means "change directory":

```bash
cd agent-harness-workshop
```

Create and switch to your exercise branch. The `-c` option means "create":

```bash
git switch -c my-workshop
```

Both branches start with the same files. Your commits will be recorded on `my-workshop`; `main` remains the starter.
Confirm you are inside the repository and on your exercise branch:

```bash
git status
```

Expect `On branch my-workshop` and `nothing to commit, working tree clean`.
If you see an error, use [troubleshooting](#troubleshooting) before continuing.

Open this same `agent-harness-workshop` folder in your editor.
Keep the terminal open in that folder for all remaining commands.
You can complete the workshop locally. You do not need to fork the repository, push changes, or create a GitHub account.
If you already have a copy with edits, clone into a different parent folder to keep that work.

## 2. Prepare Python

Use the commands for your operating system. Run one code block at a time, in order.

### macOS / Linux

Check that Python is version 3.10 or newer:

```bash
python3 --version
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

Expect **15 tests, OK**. These checks run offline and do not need an API key.
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

Run one code block at a time, in this same PowerShell terminal.
Use Python's hidden prompt to make the key available to the workshop:

```powershell
$env:GROQ_API_KEY = (& .\.venv\Scripts\python.exe -c "import getpass; print(getpass.getpass('Groq API key: '))")
```

At `Groq API key:`, paste only your key, then press Enter.
The terminal will not display the key as you type or paste it.
This command uses the virtual environment's Python directly, even if activation is blocked.

Verify that Python receives the key without displaying it:

```powershell
.\.venv\Scripts\python.exe -c "import os; print('Key length:', len(os.environ.get('GROQ_API_KEY', '').strip()))"
```

Expect `Key length:` followed by a number greater than zero.
If it is zero, repeat the hidden-prompt command before continuing.
A positive length confirms that Python receives a value; the live check below confirms whether the key works.

The key belongs to this terminal session, not the virtual environment. Closing the terminal removes it;
deactivating `.venv` does not. The application does not load `.env` files.
The supplied model is [`openai/gpt-oss-120b` on Groq](https://console.groq.com/docs/models); no model setting is required.

## 4. Check setup

Run the command for your operating system in the same terminal where you set the key.

### macOS / Linux

```bash
python workshop.py --prompt "Reply with: ready"
```

### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe workshop.py --prompt "Reply with: ready"
```

This command makes one live model request. Expect `Output:` followed by the model's text without an error.
The wording can vary. Resolve any error before class.

You are ready when you have your own branch, passing offline checks, and a successful live reply.
During class, use this terminal to run the program; an editor's Run button may not have your API key.

**Next: [start the workshop](README.md#0-try-the-starter--4-minutes).**

## Troubleshooting

| Problem | What to do |
| --- | --- |
| Missing `GROQ_API_KEY` | Repeat step 3 in the same terminal that runs Python. |
| HTTP 401 | Check that you entered a valid Groq key. |
| HTTP 400 during a tool-request step | Check for an old `GROQ_MODEL` override. Use the supplied `openai/gpt-oss-120b` default, then rerun once. Ask the instructor if it still fails. |
| HTTP 403 or unavailable model | Check your account's model access in Groq Console. |
| HTTP 429 | Pause live calls and check [Groq limits](https://console.groq.com/docs/rate-limits). Offline tests still work. |
| Invalid tool arguments | Compare `TOOLS` and the prompt with the README. The harness validates arguments before execution. |
| A step does not behave as described | Compare the entire `run_agent` function with that step's code block. |
| Indentation error | Copy the whole function block, including its spaces. Do not use tabs. |
| `git` is not recognized or not found | Install Git, then reopen your terminal and start step 1 again. |
| Git does not recognize `switch` | Update Git to version 2.23 or newer. |
| Clone says the destination already exists | You already have a folder with that name. For a fresh start, clone from a different parent folder. Keep any existing edits. |
| `fatal: not a git repository` | Open the cloned project folder in your terminal. Run `git status` there before continuing. |
| `my-workshop` branch already exists | Run `git switch my-workshop` to resume, then `git status` to confirm the branch. |
| `git status` says `On branch main` | Before editing, run `git switch -c my-workshop`. If the branch already exists, use `git switch my-workshop`. |
| Commit says `nothing to commit` | Save `workshop.py` in your editor and run `git status`. If it is modified, run `git add workshop.py` before committing. A clean status means there are no new changes to record. |
| Python cannot find `workshop.py` or `tests` | Run the command from the `agent-harness-workshop` folder. |
| A new terminal cannot find `python` or your key | Activate `.venv` and repeat step 3 in that terminal. |
| Git opens a pager | Press `q` to return to the terminal. |
| Network or certificate error | Check connectivity and your Python installation. Do not disable TLS verification. |

If you previously set `GROQ_MODEL`, remove the override to use the supplied default.
In Bash or Zsh:

```bash
unset GROQ_MODEL
```

In PowerShell:

```powershell
Remove-Item Env:GROQ_MODEL -ErrorAction SilentlyContinue
```

### Git asks for your name or email

A commit records an author name and email. These identify the checkpoint; they are not a GitHub login.
Run the commands below from the workshop folder, replacing the example values with your own.
These settings apply only to this repository.

Set your name:

```bash
git config user.name "Your Name"
```

Set your email:

```bash
git config user.email "you@example.com"
```

Then rerun the `git commit` command from the workshop instructions.

[Groq API documentation](https://console.groq.com/docs/quickstart) · [Open-Meteo documentation](https://open-meteo.com/en/docs)

Weather data by [Open-Meteo](https://open-meteo.com/), licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Retain attribution when sharing weather output.
