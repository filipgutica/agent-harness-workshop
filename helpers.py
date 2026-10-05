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


def call_model(
    messages: list[dict], *, tools: list[dict] | None = None,
    response_format: dict | None = None,
) -> dict:
    """Send history to Groq and return a validated assistant message dictionary.

    Preserve native tool_calls and their IDs, including replies with null content.
    Optional tools describe callable functions; this helper never executes them.
    Optional response_format controls a separate final-answer formatting request.
    Groq does not support combining tools and Structured Outputs in one request.
    Trace messages and request progress without logging headers or credentials.
    Raise RuntimeError for transport failures or malformed assistant envelopes.
    """
    if tools is not None and response_format is not None:
        raise ValueError("Use response_format in a separate request without tools.")
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "replace-with-your-own-key":
        raise RuntimeError("Set GROQ_API_KEY in your terminal first.")
    payload = {
        "model": os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b"),
        "messages": messages,
        "max_tokens": 2048,
    }
    if tools is not None:
        payload["tools"] = tools
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
    # Teaching labels explain API roles; the request uses system/user/assistant/tool.
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
        latest_content = latest.get("content")
        if latest_content is None:
            latest_content = json.dumps(latest.get("tool_calls", []), ensure_ascii=False)
        print_log("Model input (latest message)", f"[{label}]\n{latest_content}")
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
        choice = data["choices"][0]
        if choice.get("finish_reason") == "length":
            raise RuntimeError("Model output was truncated. Try a shorter prompt or another model.")
        message = choice["message"]
        if message["role"] != "assistant":
            raise ValueError("Expected an assistant message.")
        content = message.get("content")
        tool_calls = message.get("tool_calls")
        if content is not None and not isinstance(content, str):
            raise ValueError("Assistant content must be text or null.")
        if tool_calls is not None and not isinstance(tool_calls, list):
            raise ValueError("tool_calls must be a list.")
        if tool_calls:
            if tools is None:
                raise ValueError("Received a tool request without declaring tools.")
            ids = set()
            for tool_call in tool_calls:
                validate_tool_call(tool_call)
                if tool_call["id"] in ids:
                    raise ValueError("Tool call IDs must be unique within a reply.")
                ids.add(tool_call["id"])
        elif not content or not content.strip():
            raise ValueError("Expected assistant text or tool_calls.")
    except (KeyError, IndexError, TypeError, AttributeError, ValueError) as error:
        raise RuntimeError("Model API returned an invalid assistant message.") from error
    # Resend only conversation fields, not server metadata such as reasoning.
    reply = {"role": "assistant", "content": content}
    if tool_calls:
        reply["tool_calls"] = tool_calls
    print_log("Harness", "received the model reply; returning its assistant message.")
    return reply


def validate_tool_call(tool_call: dict) -> None:
    """Check the native request envelope before it is stored or dispatched.

    Argument JSON and the allowed function are checked by dispatch_tool.
    """
    if not isinstance(tool_call, dict) or tool_call.get("type") != "function":
        raise ValueError("Expected a function tool call.")
    if not isinstance(tool_call.get("id"), str) or not tool_call["id"].strip():
        raise ValueError("Tool call requires a nonempty ID.")
    function = tool_call.get("function")
    if (not isinstance(function, dict) or not isinstance(function.get("name"), str)
            or not function["name"].strip()):
        raise ValueError("Tool call requires a function name.")
    if not isinstance(function.get("arguments"), str):
        raise ValueError("Tool arguments must be JSON text.")


def parse_answer(raw: str) -> dict:
    """Validate the final JSON answer locally, including prompt-only JSON replies.

    Accept exactly one nonempty answer string. This validates shape, not facts.
    """
    try:
        answer = json.loads(raw)
    except (ValueError, TypeError) as error:
        raise ValueError("Return a JSON object without Markdown fences.") from error
    if not isinstance(answer, dict) or set(answer) != {"answer"}:
        raise ValueError("JSON answer requires exactly the answer field.")
    if not isinstance(answer["answer"], str) or not answer["answer"].strip():
        raise ValueError("JSON answer must contain a nonempty string.")
    return answer


def _weather_api_json(request: Request, *, service: str) -> dict:
    """Read a JSON object from either Open-Meteo API and report request failures."""
    try:
        with urlopen(request, timeout=30) as response:
            data = json.load(response)
    except HTTPError as error:
        error.close()
        raise RuntimeError(f"{service} API returned HTTP {error.code}.") from error
    except (URLError, TimeoutError) as error:
        raise RuntimeError(f"{service} API unavailable or timed out. Try again later.") from error
    except (ValueError, UnicodeError) as error:
        raise RuntimeError(f"{service} API returned invalid JSON.") from error
    if not isinstance(data, dict):
        raise RuntimeError(f"{service} API returned an invalid object.")
    return data


def get_weather(*, location: str) -> dict:
    """Look up a city's coordinates, then fetch current weather from Open-Meteo.

    Use the first geocoding match; a country or region can narrow the city name.
    Return the resolved location, readings, units, local timezone, timestamp,
    and source attribution for the model. Reject empty or unmatched locations
    with ValueError; report API failures or malformed data with RuntimeError.
    Trace both HTTP requests so students can follow the tool's work.
    """
    if not isinstance(location, str) or not location.strip():
        raise ValueError("Weather requires a nonempty city name.")
    location = location.strip()
    # The forecast API needs coordinates. Geocoding translates the city's name.
    lookup_query = urlencode({"name": location, "count": 1, "language": "en", "format": "json"})
    lookup = Request(f"https://geocoding-api.open-meteo.com/v1/search?{lookup_query}")
    endpoint = lookup.full_url.split("?", 1)[0]
    print_log("Harness", f"get_weather: {lookup.get_method()} {endpoint} (finding coordinates for {location}).")
    matches = _weather_api_json(lookup, service="Geocoding").get("results", [])
    if not isinstance(matches, list):
        raise RuntimeError("Geocoding API returned invalid location results.")
    if not matches:
        raise ValueError(f"No city found for {location!r}. Try adding a country or region.")
    city = matches[0]
    if not isinstance(city, dict) or not isinstance(city.get("name"), str) or not city["name"].strip():
        raise RuntimeError("Geocoding API returned an invalid city name.")
    # Never send missing, nonnumeric, or out-of-range coordinates to the forecast API.
    for field, lower, upper in (("latitude", -90, 90), ("longitude", -180, 180)):
        value = city.get(field)
        if type(value) not in (int, float) or not lower <= value <= upper:
            raise RuntimeError(f"Geocoding API returned an invalid {field}.")
    # Report the actual match, so similarly named cities are distinguishable.
    resolved_location = ", ".join(
        city[field].strip() for field in ("name", "admin1", "country")
        if isinstance(city.get(field), str) and city[field].strip()
    )
    query = urlencode({
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "current": "temperature_2m,apparent_temperature,precipitation",
        "timezone": "auto",  # Resolve local time from the chosen coordinates.
    })
    request = Request(f"https://api.open-meteo.com/v1/forecast?{query}")
    endpoint = request.full_url.split("?", 1)[0]
    print_log("Harness", f"get_weather: {request.get_method()} {endpoint} (current weather for {resolved_location}).")
    data = _weather_api_json(request, service="Weather")
    current = data.get("current")
    units = data.get("current_units")
    if not isinstance(current, dict) or not isinstance(units, dict):
        raise RuntimeError("Weather API response is missing current conditions or units.")
    if not isinstance(current.get("time"), str) or not current["time"].strip():
        raise RuntimeError("Weather API response is missing its timestamp.")
    if not isinstance(data.get("timezone"), str) or not data["timezone"].strip():
        raise RuntimeError("Weather API response is missing its timezone.")
    # Check that the model will receive every requested reading and its unit.
    for field in ("temperature_2m", "apparent_temperature", "precipitation"):
        if type(current.get(field)) not in (int, float) or not isinstance(units.get(field), str):
            raise RuntimeError(f"Weather API response is missing a reading or unit: {field}.")
    return {
        "location": resolved_location, "source": "Open-Meteo", "timezone": data["timezone"],
        "current": current, "units": units,
    }


def dispatch_tool(tool_call: dict) -> dict:
    """Validate and execute one native tool call through the local allowlist.

    The API supplies function.arguments as JSON text. Decode it, require exactly
    one nonempty location string, and call a known function. Never evaluate model
    code. Raise ValueError for invalid requests; tool/API errors propagate.
    """
    validate_tool_call(tool_call)
    tools = {"get_weather": get_weather}
    function = tool_call["function"]
    tool_name = function["name"]
    if tool_name not in tools:
        raise ValueError(f"Unknown tool: {tool_name}")
    try:
        parameters = json.loads(function["arguments"])
    except ValueError as error:
        raise ValueError("Tool arguments must be valid JSON.") from error
    if (not isinstance(parameters, dict) or set(parameters) != {"location"}
            or not isinstance(parameters["location"], str) or not parameters["location"].strip()):
        raise ValueError("get_weather requires exactly one nonempty string parameter: location.")
    # Choose a registered function; never execute code supplied by the model.
    return tools[tool_name](location=parameters["location"])


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
