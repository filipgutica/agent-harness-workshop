"""Supplied HTTP, validation, and terminal helpers. You only edit workshop.py."""

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def _format_label(label: str) -> str:
    """Style a prompt or log label when its output stream supports color."""
    stream = sys.stderr if label == "Error" else sys.stdout
    styles = {
        "You": "1;34",
        "Harness": "2",
        "Model input (latest message)": "36",
        "Model reply (raw)": "36",
        "Tool result (data)": "33",
        "Output": "1;32",
        "Error": "1;31",
    }
    heading = f"{label}:"
    # Terminal colors are decoration; labels still identify every message without them.
    if stream.isatty() and "NO_COLOR" not in os.environ and os.environ.get("TERM") != "dumb":
        heading = f"\033[{styles.get(label, '2')}m{heading}\033[0m"
    return heading


def print_log(label: str, message: str) -> None:
    """Print a labeled terminal message with readable indentation and color.

    Internal processing is indented; Output and Error stay at the left edge.
    Indent continuation lines beneath their message. Color only the label,
    using the terminal's palette. Redirected output, NO_COLOR, and TERM=dumb
    stay plain text. Error messages use stderr; other messages use stdout.
    This helper changes presentation only, not model messages or tool data.
    """
    stream = sys.stderr if label == "Error" else sys.stdout
    indent = "" if label in ("Output", "Error") else "  "
    heading = _format_label(label)
    lines = message.splitlines() or [""]
    print(f"{indent}{heading} {lines[0]}", file=stream, flush=True)
    for line in lines[1:]:
        print(f"{indent}  {line}", file=stream, flush=True)


def call_model(messages: list[dict[str, str]], *, response_format: dict | None = None) -> str:
    """Send the conversation to Groq and return the assistant's text.

    Read the API key and optional model override from the terminal environment.
    Forward response_format when the optional exercise requests JSON or a schema.
    Without it, use ordinary text output for the core exercise.
    Trace the outgoing message count, named roles, and latest content, then show
    when the request waits for and receives a reply. Never log HTTP headers.
    Raise RuntimeError if the request fails or the reply has no usable text.
    This function does not interpret tool requests or execute tools.
    """
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "replace-with-your-own-key":
        raise RuntimeError("Set GROQ_API_KEY in your terminal first.")
    payload = {
        "model": os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b"),
        "messages": messages,
        "max_tokens": 2048,
    }
    if response_format is not None:
        payload["response_format"] = response_format
    request = Request(
        "https://api.groq.com/openai/v1/chat/completions",
        # HTTP carries JSON bytes; the rest of the workshop uses Python objects.
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # Identify this client; Groq rejects urllib's default User-Agent.
            "User-Agent": "agent-harness-workshop/1.0",
        },
        method="POST",
    )
    # Appending messages changes a Python list, not the remote model's state.
    # Every HTTP request resends the full list, including any new tool result.
    # These teaching labels explain API roles; the request still uses system/user/assistant.
    role_labels = {
        "system": "SYSTEM_PROMPT",
        "user": "USER_MESSAGE",
        "assistant": "ASSISTANT_MESSAGE",
        "tool": "TOOL_MESSAGE",
    }
    message_labels = " + ".join(
        f"[{role_labels.get(message['role'], message['role'].upper())}]"
        for message in messages
    )
    noun = "message" if len(messages) == 1 else "messages"
    print_log("Harness", f"sending {message_labels} to {payload['model']} ({len(messages)} {noun}).")
    if messages:
        latest = messages[-1]
        label = role_labels.get(latest["role"], latest["role"].upper())
        print_log("Model input (latest message)", f"[{label}]\n{latest['content']}")
    print_log("Harness", "waiting for the model reply...")
    try:
        with urlopen(request, timeout=30) as response:
            data = json.load(response)
    except HTTPError as error:
        error.close()
        if error.code == 400:
            raise RuntimeError(
                "Model API returned HTTP 400. Check the request format and model compatibility. "
                "See SETUP.md troubleshooting."
            ) from error
        raise RuntimeError(
            f"Model API returned HTTP {error.code}. Check your key, model, and quota."
        ) from error
    except (URLError, TimeoutError) as error:
        raise RuntimeError("Model API unavailable or timed out. Try again later.") from error
    except (ValueError, UnicodeError) as error:
        raise RuntimeError("Model API returned an invalid JSON response.") from error
    try:
        # Groq wraps the assistant's text inside choices[0].message.content.
        choice = data["choices"][0]
        if choice.get("finish_reason") == "length":
            raise RuntimeError("Model output was truncated. Try a shorter prompt or another model.")
        content = choice["message"]["content"]
    except (KeyError, IndexError, TypeError, AttributeError) as error:
        raise RuntimeError("Model API response did not contain assistant content.") from error
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Model API returned empty assistant content. Try another model.")
    print_log("Harness", "received the model reply; returning its text.")
    return content


def parse_action(raw: str) -> dict:
    """Convert model text into a validated response or tool-call dictionary.

    Require the workshop's agreed JSON fields before the harness uses them.
    Raise ValueError for invalid JSON or an unexpected shape. Tool names and
    tool-specific arguments are checked separately by dispatch_tool.
    """
    try:
        action = json.loads(raw)
    except ValueError as error:
        raise ValueError("Model output must be a JSON object without Markdown fences.") from error
    if not isinstance(action, dict):
        raise ValueError("Action must be a JSON object.")
    if action.get("action") == "response":
        if set(action) != {"action", "content"}:
            raise ValueError("Response requires exactly action and content.")
        if not isinstance(action["content"], str) or not action["content"].strip():
            raise ValueError("Response content must be a nonempty string.")
    elif action.get("action") == "tool-call":
        if set(action) != {"action", "tool", "parameters"}:
            raise ValueError("Tool call requires exactly action, tool, and parameters.")
        if not isinstance(action["tool"], str) or not action["tool"].strip():
            raise ValueError("Tool must be a nonempty string.")
        if not isinstance(action["parameters"], dict):
            raise ValueError("Tool parameters must be an object.")
    else:
        raise ValueError("Unknown action. Expected response or tool-call.")
    return action


def get_weather(*, location: str) -> dict:
    """Fetch current weather estimates for Vancouver from Open-Meteo.

    Return readings, units, a timestamp, and source attribution for the model.
    Reject other locations with ValueError; report API failures or missing data
    with RuntimeError. Fixed coordinates keep this workshop to one city.
    Trace the HTTP method and API endpoint before making the weather request.
    """
    if not isinstance(location, str) or location.strip().lower() != "vancouver":
        raise ValueError("Weather supports only Vancouver.")
    query = urlencode({
        "latitude": 49.2827,
        "longitude": -123.1207,
        "current": "temperature_2m,apparent_temperature,precipitation",
        "timezone": "America/Vancouver",
    })
    request = Request(f"https://api.open-meteo.com/v1/forecast?{query}")
    # Show the tool's actual API call after the harness accepts the model's request.
    endpoint = request.full_url.split("?", 1)[0]
    print_log("Harness", f"get_weather: {request.get_method()} {endpoint} (current weather for Vancouver).")
    try:
        with urlopen(request, timeout=30) as response:
            data = json.load(response)
    except HTTPError as error:
        error.close()
        raise RuntimeError(f"Weather API returned HTTP {error.code}.") from error
    except (URLError, TimeoutError) as error:
        raise RuntimeError("Weather API unavailable or timed out. Try again later.") from error
    except (ValueError, UnicodeError) as error:
        raise RuntimeError("Weather API returned invalid JSON.") from error
    if not isinstance(data, dict):
        raise RuntimeError("Weather API returned an invalid object.")
    current = data.get("current")
    units = data.get("current_units")
    if not isinstance(current, dict) or not isinstance(units, dict):
        raise RuntimeError("Weather API response is missing current conditions or units.")
    if not isinstance(current.get("time"), str) or not current["time"].strip():
        raise RuntimeError("Weather API response is missing its timestamp.")
    # Check that the model will receive every requested reading and its unit.
    for field in ("temperature_2m", "apparent_temperature", "precipitation"):
        if type(current.get(field)) not in (int, float) or not isinstance(units.get(field), str):
            raise RuntimeError(f"Weather API response is missing a reading or unit: {field}.")
    return {"location": "Vancouver", "source": "Open-Meteo", "current": current, "units": units}


def dispatch_tool(action: dict) -> dict:
    """Execute an allowed tool request after parse_action validates its shape.

    Check the tool name and its arguments, then return the tool's result.
    Raise ValueError for an unknown tool or invalid arguments. The registry
    below is the list of functions the model may request; the harness runs them.
    """
    tools = {"get_weather": get_weather}
    tool_name = action["tool"]
    if tool_name not in tools:
        raise ValueError(f"Unknown tool: {tool_name}")
    parameters = action["parameters"]
    if set(parameters) != {"location"} or not isinstance(parameters["location"], str):
        raise ValueError("get_weather requires exactly one string parameter: location.")
    # Look up a known function rather than executing code supplied by the model.
    return tools[tool_name](location=parameters['location'])


def run_cli(answer):
    """Read questions and print each value returned by the student's function.

    The answer argument is a function, such as run_agent, supplied by workshop.py.
    Label its return value Output: because it can be model text, tool data, or
    a final answer, depending on the workshop stage. This helper does not make
    an additional model call or interpret the returned value.
    With --prompt, answer once and exit with status 1 for expected errors.
    Otherwise, keep prompting until /exit, /quit, EOF, or Ctrl-C. Show expected
    errors and let the user try again. Each question calls answer separately;
    this helper does not retain conversation history.
    Keeping terminal handling here lets students focus on the agent loop.
    """
    parser = argparse.ArgumentParser(description="Ask your workshop assistant a question.")
    parser.add_argument("--prompt", help="Omit to type your question interactively")
    args = parser.parse_args()
    try:
        if args.prompt is None:
            print("Type '/exit' or '/quit' to leave.")
        while True:
            # --prompt supplies one question; interactive mode reads a new one each time.
            question = args.prompt if args.prompt is not None else input(f"{_format_label('You')} ")
            # Handle terminal commands locally rather than sending them to the model.
            if args.prompt is None and question.strip().lower() in ("/exit", "/quit"):
                print("Goodbye.")
                return
            try:
                if not question.strip():
                    raise ValueError("Please enter a nonempty prompt.")
                # answer runs the student's code; run_cli only prints its return value.
                print_log("Output", answer(question))
            except (ValueError, RuntimeError) as error:
                print_log("Error", str(error))
                # A one-shot command must report failure; interactive users can retry.
                if args.prompt is not None:
                    raise SystemExit(1) from error
            if args.prompt is not None:
                # Without --prompt, the loop continues to the next input instead.
                return
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")
