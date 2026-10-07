import unittest
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


if __name__ == "__main__":
    unittest.main()
