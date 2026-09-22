from helpers import call_model, run_cli

SYSTEM_PROMPT = "You are a helpful assistant."


def run_agent(question):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    return call_model(messages)


if __name__ == "__main__":
    run_cli(run_agent)
