from helpers import call_model, run_cli


SYSTEM_PROMPT = "You are a helpful assistant."


def run_agent(question):
    """Send one question to the model and return its answer text.

    The helper returns an assistant message dictionary. This starter reads its
    content; later we will also handle tool_calls and add a bounded tool loop.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    reply = call_model(messages)
    return reply["content"]


if __name__ == "__main__":
    run_cli(run_agent)
