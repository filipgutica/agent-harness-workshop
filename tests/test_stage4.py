import json
import unittest
from copy import deepcopy
from unittest.mock import patch

import workshop


class RunAgentTests(unittest.TestCase):
    def test_run_agent_returns_a_direct_model_response(self):
        calls = []

        def fake_call_model(messages):
            calls.append(deepcopy(messages))
            return '{"action":"response","content":"No tool was needed."}'

        with patch.object(workshop, "call_model", side_effect=fake_call_model):
            result = workshop.run_agent("Say hello")

        self.assertEqual(result, "No tool was needed.")
        self.assertEqual(len(calls), 1)

    def test_run_agent_puts_tool_results_back_into_conversation(self):
        tool_call = (
            '{"action":"tool-call","tool":"get_weather",'
            '"parameters":{"location":"Vancouver"}}'
        )
        final_response = '{"action":"response","content":"It is 14.5 C."}'
        calls = []

        def fake_call_model(messages):
            calls.append(deepcopy(messages))
            return tool_call if len(calls) == 1 else final_response

        tool_result = {
            "location": "Vancouver",
            "source": "test",
            "current": {"temperature_2m": 14.5},
            "units": {"temperature_2m": "°C"},
        }
        with patch.object(workshop, "call_model", side_effect=fake_call_model), patch.object(
            workshop, "get_weather", return_value=tool_result
        ):
            result = workshop.run_agent("What is the weather in Vancouver?")

        self.assertEqual(result, "It is 14.5 C.")
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1][:2], calls[0])
        self.assertEqual(calls[1][2], {"role": "assistant", "content": tool_call})
        self.assertEqual(calls[1][3]["role"], "user")
        tool_message = calls[1][3]
        self.assertEqual(
            json.loads(tool_message["content"]),
            {"tool_result": {"tool": "get_weather", "result": tool_result}},
        )


if __name__ == "__main__":
    unittest.main()
