# Workshop setup

Complete this page before the workshop. Class time assumes that Python, Git, and a Groq API key are ready. Keep the terminal where you set the key open during the exercise.

## Requirements

- Python 3.10 or newer
- Git
- A Groq account and API key
- A terminal with internet access

The workshop has no third-party Python packages. The application uses `urllib.request` and `unittest` from the standard library.

## Install Python and Git

Install Python 3.10 or newer and Git before class. Use the version commands below to check them:

### macOS or Linux

```bash
python3 --version
git --version
```

### Windows PowerShell

```powershell
py -3 --version
git --version
```

If a version command fails, finish the installation before class. Ask your instructor which installer to use for your operating system.

## Create a Groq key

Create a key at the [Groq Console API keys page](https://console.groq.com/keys). Do not share the key with classmates. Do not commit it or paste it into a source file.

The application sends raw `POST` requests to Groq's OpenAI-compatible chat completions endpoint. The default model is `openai/gpt-oss-20b`. Model access and rate limits can change; check the [Groq quickstart](https://console.groq.com/docs/quickstart) and [current rate limits](https://console.groq.com/docs/rate-limits) if a request fails.

## Get the repository

For a class copy, replace `YOUR_REPOSITORY_URL` with the URL from your instructor:

```bash
git clone YOUR_REPOSITORY_URL ~/code/agent-harness-workshop
cd ~/code/agent-harness-workshop
git switch main
```

Create your student branch in the [README](README.md) after setup. Use a short branch name with no spaces.

For the local instructor copy, use:

```bash
cd ~/code/agent-harness-workshop
git switch main
```

Run later commands from the repository directory. If the directory already exists, do not clone over it. Ask the instructor for the correct local path.

## Prepare Python in the repository

Run these commands after entering the repository directory.
The virtual environment makes `python` refer to the interpreter used for this workshop.

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python --version
```

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe` instead of `python` in every workshop command.
No execution-policy change is needed.

## Set the key for one terminal session

The application reads `GROQ_API_KEY` and `GROQ_MODEL` from the environment. The example file is a reference only. Python does not load `.env.example` automatically.

### macOS or Linux

Open a temporary Bash shell. The hidden prompt keeps the key out of shell history:

```bash
bash
read -r -s -p "Groq API key: " GROQ_API_KEY
printf '\n'
export GROQ_API_KEY
export GROQ_MODEL=openai/gpt-oss-20b
```

Keep using this terminal for the workshop. When you run `exit`, the temporary shell and its key variable are discarded.

### Windows PowerShell

Use a secure prompt. The key is stored in the environment for the current PowerShell window:

```powershell
$secret = Read-Host "Groq API key" -AsSecureString
$env:GROQ_API_KEY = [System.Net.NetworkCredential]::new('', $secret).Password
Remove-Variable secret
$env:GROQ_MODEL = 'openai/gpt-oss-20b'
```

Keep this PowerShell window open for the workshop.

## Check the starter

Run these commands from the repository directory. They do not make a model request:

```bash
python workshop.py --mode echo --prompt "Hello, harness"
python -m unittest tests.test_cli tests.test_model tests.test_protocol -v
```

The echo command must print `Echo: Hello, harness`. The supplied tests use fake responses, so they do not spend API quota.

If Git asks for your identity at the first commit, set it for this repository and retry:

```bash
git config user.name "Your Name"
git config user.email "your-email@example.com"
```

## Weather data

The `get_weather` tool sends Vancouver coordinates to Open-Meteo. It uses current modelled conditions and preserves the returned time, units, and source. See the [Open-Meteo API documentation](https://open-meteo.com/en/docs). Weather data by [Open-Meteo](https://open-meteo.com/), licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Retain this attribution when sharing weather output.

## Troubleshooting

- `Set GROQ_API_KEY` means the key is missing from the current terminal. Set it again and run the command in that same terminal.
- For HTTP 401, check your Groq key. For 403, check account and model access. For 429, pause live calls and check the [current rate limits](https://console.groq.com/docs/rate-limits).
- If `--mode action` prints invalid JSON, check that you copied the full `SYSTEM_PROMPT` block. The model can still vary its output; retry once and inspect the raw `Model:` line.
- A weather API error usually means the network request failed. Check internet access and retry.
- If `python` is not available, use `python3` on macOS or Linux, or `py -3` on Windows. If activation failed, use the executable inside `.venv`.
