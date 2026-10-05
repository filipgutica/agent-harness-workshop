import json
import unittest
from copy import deepcopy
from unittest.mock import patch

import helpers
import workshop
from tests.support import native_tool_call


class RunAgentTests(unittest.TestCase):
    def test_run_agent_returns_a_direct_model_response(self):
        calls = []
        def fake_call_model(messages, *, tools=None):
            calls.append(deepcopy(messages))
            self.assertEqual(tools, workshop.TOOLS)
            return {"role": "assistant", "content": "No tool was needed."}
        with patch.object(workshop, "call_model", side_effect=fake_call_model):
            result = workshop.run_agent("Say hello")
        self.assertEqual(result, "No tool was needed.")
        self.assertEqual(calls, [[
            {"role": "system", "content": workshop.SYSTEM_PROMPT},
            {"role": "user", "content": "Say hello"},
        ]])

    def test_run_agent_returns_matching_tool_messages_for_each_request(self):
        tool_calls = [native_tool_call(), native_tool_call(call_id="call_paris", arguments='{"location":"Paris, France"}')]
        assistant = {"role": "assistant", "content": None, "tool_calls": tool_calls}
        calls = []
        def fake_call_model(messages, *, tools=None):
            calls.append(deepcopy(messages))
            return assistant if len(calls) == 1 else {"role": "assistant", "content": "Both cities are mild."}
        results = [{"location": "Vancouver", "temperature": 14.5}, {"location": "Paris", "temperature": 17}]
        with patch.object(workshop, "call_model", side_effect=fake_call_model), patch.object(
            helpers, "get_weather", side_effect=results
        ) as weather:
            result = workshop.run_agent("Compare Vancouver and Paris weather")
        self.assertEqual(result, "Both cities are mild.")
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1][:2], calls[0])
        self.assertEqual(calls[1][2], assistant)
        self.assertEqual(calls[1][3:], [
            {"role": "tool", "tool_call_id": "call_weather", "content": json.dumps(results[0], ensure_ascii=False)},
            {"role": "tool", "tool_call_id": "call_paris", "content": json.dumps(results[1], ensure_ascii=False)},
        ])
        self.assertEqual([call.kwargs for call in weather.call_args_list], [{"location": "Vancouver"}, {"location": "Paris, France"}])


if __name__ == "__main__":
    unittest.main()
