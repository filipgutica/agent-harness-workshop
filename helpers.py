"""Supplied HTTP, validation, and terminal helpers. You only edit workshop.py."""

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def call_model(messages: list[dict[str, str]]) -> str:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "replace-with-your-own-key":
        raise RuntimeError("Set GROQ_API_KEY in your terminal first.")
    payload = {
        "model": os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b"),
        "messages": messages,
        "max_tokens": 2048,
    }
    request = Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            data = json.load(response)
    except HTTPError as error:
        error.close()
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
        content = choice["message"]["content"]
    except (KeyError, IndexError, TypeError, AttributeError) as error:
        raise RuntimeError("Model API response did not contain assistant content.") from error
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Model API returned empty assistant content. Try another model.")
    return content


def parse_action(raw: str) -> dict:
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
    if not isinstance(location, str) or location.strip().lower() != "vancouver":
        raise ValueError("Weather supports only Vancouver.")
    query = urlencode({
        "latitude": 49.2827,
        "longitude": -123.1207,
        "current": "temperature_2m,apparent_temperature,precipitation",
        "timezone": "America/Vancouver",
    })
    request = Request(f"https://api.open-meteo.com/v1/forecast?{query}")
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
    for field in ("temperature_2m", "apparent_temperature", "precipitation"):
        if type(current.get(field)) not in (int, float) or not isinstance(units.get(field), str):
            raise RuntimeError(f"Weather API response is missing a reading or unit: {field}.")
    return {"location": "Vancouver", "source": "Open-Meteo", "current": current, "units": units}


def dispatch_tool(action: dict) -> dict:
    tools = {"get_weather": get_weather}
    tool_name = action["tool"]
    if tool_name not in tools:
        raise ValueError(f"Unknown tool: {tool_name}")
    parameters = action["parameters"]
    if set(parameters) != {"location"} or not isinstance(parameters["location"], str):
        raise ValueError("get_weather requires exactly one string parameter: location.")
    # Checkpoint 2: Call the registered tool with the validated location.
    return tools[tool_name](location=parameters['location'])


def run_cli(answer):
    """Read one question, call the student's function, and print its answer."""
    parser = argparse.ArgumentParser(description="Ask your workshop assistant a question.")
    parser.add_argument("--prompt", help="Omit to type your question interactively")
    args = parser.parse_args()
    try:
        question = args.prompt if args.prompt is not None else input("You: ")
        if not question.strip():
            raise ValueError("Please enter a nonempty prompt.")
        print("Assistant:", answer(question))
    except (ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")
