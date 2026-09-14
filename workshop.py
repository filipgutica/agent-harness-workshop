"""Build a small agent harness. Follow README.md in checkpoint order."""

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


MAX_STEPS = 5
SYSTEM_PROMPT = "You are a helpful assistant."


def call_model(messages: list[dict[str, str]]) -> str:
    # TODO 1: Send messages to OpenRouter and return assistant content.
    raise NotImplementedError("Complete checkpoint 1: call_model")


def parse_action(raw: str) -> dict:
    # TODO 2: Decode JSON and validate the two allowed action shapes.
    raise NotImplementedError("Complete checkpoint 2: parse_action")


def get_weather(*, location: str) -> dict:
    # TODO 3: Fetch current weather for Vancouver from Open-Meteo.
    raise NotImplementedError("Complete checkpoint 3: get_weather")


def dispatch_tool(action: dict) -> dict:
    # TODO 3: Validate the tool name and parameters, then call the function.
    raise NotImplementedError("Complete checkpoint 3: dispatch_tool")


def run_agent(prompt: str) -> str:
    # TODO 4: Implement the loop. TODO 5: Bound it with MAX_STEPS.
    raise NotImplementedError("Complete checkpoint 4: run_agent")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["echo", "chat", "action", "agent"], default="echo")
    parser.add_argument("--prompt", help="Omit to type a prompt interactively")
    args = parser.parse_args()
    try:
        prompt = args.prompt if args.prompt is not None else input("You: ")
        if not prompt.strip():
            raise ValueError("Please enter a nonempty prompt.")
        if args.mode == "echo":
            print(f"Echo: {prompt}")
        elif args.mode == "chat":
            print(call_model([
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]))
        elif args.mode == "action":
            raw = call_model([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ])
            print("Model:", raw)
            print("Validated action:", json.dumps(parse_action(raw), indent=2))
        else:
            print("Assistant:", run_agent(prompt))
    except (ValueError, RuntimeError, NotImplementedError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
