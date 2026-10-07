from helpers import call_model, print_log, run_cli


SYSTEM_PROMPT = "You are a helpful assistant."


def run_agent(question):
    """Send one question to the model and return its answer text."""
    # 1. Give the model instructions and the user's question.
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    # 2. Send these messages. The helper returns an assistant message dictionary.
    reply = call_model(messages)
    print_log("Model reply (raw)", str(reply))
    # 3. Return its answer text for the CLI to print.
    return reply["content"]


if __name__ == "__main__":
    run_cli(run_agent)
