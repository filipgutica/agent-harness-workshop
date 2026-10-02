from helpers import call_model, run_cli

SYSTEM_PROMPT = "You are a helpful assistant."


def run_agent(question):
    """Send one question to the model and return its text reply.

    This starter makes one model call. We will add tool execution and a loop.
    """
    messages = [
        # The system message sets the instructions; the user message asks the question.
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    return call_model(messages)


if __name__ == "__main__":
    run_cli(run_agent)
