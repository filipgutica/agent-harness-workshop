import json
import unittest
from copy import deepcopy
from unittest.mock import patch

import helpers
import workshop


class HarnessSafetyTests(unittest.TestCase):
    def test_run_agent_stops_after_the_maximum_number_of_tool_steps(self):
        tool_call = (
            '{"action":"tool-call","tool":"get_weather",'
            '"parameters":{"location":"Vancouver"}}'
        )

        for invalid_count in (0, workshop.MAX_RETRIES):
            with self.subTest(invalid_count=invalid_count):
                replies = (["not JSON"] * invalid_count + [tool_call]) * workshop.MAX_STEPS
                with patch.object(workshop, "call_model", side_effect=replies) as model, patch.object(
                    workshop, "dispatch_tool", return_value={"ok": True}
                ) as dispatch:
                    with self.assertRaises(RuntimeError):
                        workshop.run_agent("Keep checking")

                self.assertEqual(model.call_count, workshop.MAX_STEPS * (invalid_count + 1))
                self.assertEqual(dispatch.call_count, workshop.MAX_STEPS)

    def test_run_agent_does_not_execute_an_invalid_tool(self):
        invalid_tool = (
            '{"action":"tool-call","tool":"delete_everything",'
            '"parameters":{}}'
        )

        with patch.object(workshop, "call_model", return_value=invalid_tool) as model, patch.object(
            helpers, "get_weather"
        ) as weather:
            with self.assertRaises(ValueError):
                workshop.run_agent("Do something dangerous")

        weather.assert_not_called()
        model.assert_called_once()

    def test_run_agent_stops_after_the_maximum_number_of_format_retries(self):
        for max_retries in (0, workshop.MAX_RETRIES):
            with self.subTest(max_retries=max_retries), patch.object(
                workshop, "MAX_RETRIES", max_retries
            ), patch.object(workshop, "call_model", return_value="not JSON") as model, patch.object(
                helpers, "get_weather"
            ) as weather:
                with self.assertRaisesRegex(RuntimeError, "retries"):
                    workshop.run_agent("Use a tool")

                self.assertEqual(model.call_count, max_retries + 1)
                weather.assert_not_called()

    def test_run_agent_requests_a_correction_after_invalid_model_output(self):
        valid_reply = '{"action":"response","content":"Corrected answer."}'
        invalid_replies = [
            "not JSON",
            f"```json\n{valid_reply}\n```",
            '{"action":"response","content":42}',
        ]
        for invalid_reply in invalid_replies:
            with self.subTest(invalid_reply=invalid_reply):
                calls = []
                replies = iter([invalid_reply, valid_reply])

                def fake_call_model(messages, *, response_format=None):
                    calls.append(deepcopy(messages))
                    return next(replies)

                with patch.object(workshop, "call_model", side_effect=fake_call_model), patch.object(
                    helpers, "get_weather"
                ) as weather:
                    result = workshop.run_agent("Say hello")

                self.assertEqual(result, "Corrected answer.")
                self.assertEqual(len(calls), 2)
                self.assertEqual(calls[1][:2], calls[0])
                self.assertEqual(calls[1][2], {"role": "assistant", "content": invalid_reply})
                self.assertEqual(calls[1][3]["role"], "user")
                self.assertIn("JSON", calls[1][3]["content"])
                weather.assert_not_called()

    def test_run_agent_does_not_retry_model_or_weather_failures(self):
        tool_call = json.dumps({
            "action": "tool-call", "tool": "get_weather", "parameters": {"location": "Vancouver"},
        })
        for source, error in (
            ("model", RuntimeError("Model API unavailable")),
            ("weather", RuntimeError("Weather API unavailable")),
            ("weather", ValueError("No city found.")),
        ):
            with self.subTest(source=source, error=error):
                with patch.object(workshop, "call_model") as model, patch.object(
                    helpers, "get_weather", side_effect=error
                ) as weather:
                    if source == "model":
                        model.side_effect = error
                    else:
                        model.return_value = tool_call
                    with self.assertRaises(type(error)) as raised:
                        workshop.run_agent("Check Vancouver weather")

                self.assertIs(raised.exception, error)
                model.assert_called_once()
                if source == "model":
                    weather.assert_not_called()
                else:
                    weather.assert_called_once_with(location="Vancouver")


if __name__ == "__main__":
    unittest.main()
