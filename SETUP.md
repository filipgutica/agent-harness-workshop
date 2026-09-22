# Setup before class

You need **Python 3.10+**, **Git**, a **Groq API key**, and internet access.
There are no Python packages to install. Allow extra time for account creation and software installation.

## 1. Clone the workshop

On the GitHub repository page, select **Code → HTTPS** and copy the clone URL.
Replace `REPOSITORY_URL` below with that URL. Run these commands in a directory where you keep projects:

```bash
git clone REPOSITORY_URL agent-harness-workshop
cd agent-harness-workshop
```

Already have a local copy? Open its directory instead. Keep using this terminal for the remaining steps.
Use a fresh clone for a trial run so you start with the student version on `main`.

## 2. Prepare Python

Use the commands for your operating system.

### macOS / Linux

```bash
python3 --version
git --version
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
py -3 --version
git --version
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If activation is blocked, use `.\.venv\Scripts\python.exe` instead of `python` in every later command.
You do not need to change the execution policy.

If Python or Git is missing, install it before continuing.

## 3. Set your Groq key

Create a key at [Groq Console](https://console.groq.com/keys).
Enter it through the hidden prompt below. Do not paste it into source files or commits.

### macOS / Linux

```bash
bash
read -r -s -p "Groq API key: " GROQ_API_KEY
printf '\n'
export GROQ_API_KEY
```

Stay in this Bash shell for the workshop. Running `exit` discards its key variable.

### Windows PowerShell

```powershell
$secret = Read-Host "Groq API key" -AsSecureString
$env:GROQ_API_KEY = [System.Net.NetworkCredential]::new('', $secret).Password
Remove-Variable secret
```

The key lasts for this terminal session. The application does not load `.env` files.
The supplied model is `openai/gpt-oss-20b` on Groq; no model setting is required.

## 4. Check setup

```bash
python -m unittest tests.test_cli tests.test_model tests.test_protocol -q
python workshop.py --mode chat --prompt "Reply with: ready"
```

The offline checks should report **10 tests, OK**. The second command makes one live model request.
It should print a short reply without an error. Resolve any error before class.

**Next: [start the workshop](README.md#0-start-and-ask-a-question).**

## Troubleshooting

| Problem | What to do |
| --- | --- |
| Missing `GROQ_API_KEY` | Repeat step 3 in the same terminal that runs Python. |
| HTTP 401 | Check that you entered a valid Groq key. |
| HTTP 403 or unavailable model | Check your account's model access in Groq Console. |
| HTTP 429 | Pause live calls and check [Groq limits](https://console.groq.com/docs/rate-limits). Offline tests still work. |
| Invalid JSON in action mode | Copy the full system prompt again, then retry once. Ask the instructor if it still fails. |
| `Complete checkpoint ...` | Replace the indicated TODO's `raise` line; do not add code below it. |
| Indentation error | Use four spaces at TODO 2 and eight at TODOs 3a–3c. Do not use tabs. |
| `my-workshop` branch already exists | Run `git switch my-workshop` to resume. |
| Git opens a pager | Press `q` to return to the terminal. |
| Network or certificate error | Check connectivity and your Python installation. Do not disable TLS verification. |

If Git asks for your identity, run these with your own details, then retry the commit:

```bash
git config user.name "Your Name"
git config user.email "you@example.com"
```

[Groq API documentation](https://console.groq.com/docs/quickstart) · [Open-Meteo documentation](https://open-meteo.com/en/docs)

Weather data by [Open-Meteo](https://open-meteo.com/), licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Retain attribution when sharing weather output.
