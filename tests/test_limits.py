import unittest
from copy import deepcopy
from unittest.mock import patch

import helpers
import workshop
from tests.support import native_tool_call


class HarnessSafetyTests(unittest.TestCase):
    def test_run_agent_stops_after_the_maximum_number_of_tool_steps(self):
        reply = {"role": "assistant", "content": None, "tool_calls": [native_tool_call()]}
        with patch.object(workshop, "call_model", return_value=reply) as model, patch.object(
            workshop, "dispatch_tool", return_value={"ok": True}
        ) as dispatch:
            with self.assertRaises(RuntimeError):
                workshop.run_agent("Keep checking")
        self.assertEqual(model.call_count, workshop.MAX_STEPS)
        self.assertEqual(dispatch.call_count, workshop.MAX_STEPS)

    def test_run_agent_does_not_execute_an_unknown_tool(self):
        reply = {"role": "assistant", "content": None, "tool_calls": [native_tool_call(name="delete_everything")]}
        with patch.object(workshop, "call_model", return_value=reply) as model, patch.object(helpers, "get_weather") as weather:
            with self.assertRaises(ValueError):
                workshop.run_agent("Do something dangerous")
        weather.assert_not_called()
        model.assert_called_once()

    def test_format_answer_stops_after_the_maximum_number_of_retries(self):
        for max_retries in (0, 2):
            with self.subTest(max_retries=max_retries), patch.object(workshop, "MAX_RETRIES", max_retries), patch.object(
                workshop, "call_model", return_value={"role": "assistant", "content": "not JSON"}
            ) as model:
                with self.assertRaisesRegex(RuntimeError, "retries"):
                    workshop.format_answer("A supplied answer")
            self.assertEqual(model.call_count, max_retries + 1)

    def test_format_answer_requests_corrections_without_tools(self):
        for invalid in ("not JSON", '{"answer":42}'):
            calls = []
            replies = iter([{"role": "assistant", "content": invalid}, {"role": "assistant", "content": '{"answer":"Corrected answer."}'}])
            def fake_call_model(messages, **kwargs):
                calls.append((deepcopy(messages), kwargs))
                return next(replies)
            with self.subTest(invalid=invalid), patch.object(workshop, "call_model", side_effect=fake_call_model):
                result = workshop.format_answer("Corrected answer.")
            self.assertEqual(result, '{"answer": "Corrected answer."}')
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[1][0][:2], calls[0][0])
            self.assertEqual(calls[1][0][2], {"role": "assistant", "content": invalid})
            self.assertEqual(calls[1][0][3]["role"], "user")
            self.assertIn("JSON", calls[1][0][3]["content"])
            self.assertTrue(all("tools" not in kwargs for _, kwargs in calls))

    def test_run_agent_does_not_retry_model_or_weather_failures(self):
        for source, error in (("model", RuntimeError("Model API unavailable")),
                              ("weather", RuntimeError("Weather API unavailable")),
                              ("weather", ValueError("No city found"))):
            reply = {"role": "assistant", "content": None, "tool_calls": [native_tool_call()]}
            with self.subTest(source=source), patch.object(workshop, "call_model", return_value=reply) as model, patch.object(
                helpers, "get_weather", side_effect=error
            ) as weather:
                if source == "model":
                    model.side_effect = error
                with self.assertRaises(type(error)) as raised:
                    workshop.run_agent("Weather in Vancouver?")
            self.assertIs(raised.exception, error)
            model.assert_called_once()
            self.assertEqual(weather.call_count, int(source == "weather"))

    def test_formatter_does_not_retry_api_failures(self):
        error = RuntimeError("Model API unavailable")
        with patch.object(workshop, "call_model", side_effect=error) as model:
            with self.assertRaises(RuntimeError) as raised:
                workshop.format_answer("Supplied answer")
        self.assertIs(raised.exception, error)
        model.assert_called_once()


if __name__ == "__main__":
    unittest.main()
