import unittest
from unittest.mock import patch

import helpers
import workshop


class HarnessSafetyTests(unittest.TestCase):
    def test_run_agent_stops_after_the_maximum_number_of_tool_steps(self):
        tool_call = (
            '{"action":"tool-call","tool":"get_weather",'
            '"parameters":{"location":"Vancouver"}}'
        )

        with patch.object(workshop, "call_model", return_value=tool_call) as model, patch.object(
            workshop, "dispatch_tool", return_value={"ok": True}
        ) as dispatch:
            with self.assertRaises(RuntimeError):
                workshop.run_agent("Keep checking")

        self.assertEqual(model.call_count, workshop.MAX_STEPS)
        self.assertEqual(dispatch.call_count, workshop.MAX_STEPS)

    def test_run_agent_does_not_execute_an_invalid_tool(self):
        invalid_tool = (
            '{"action":"tool-call","tool":"delete_everything",'
            '"parameters":{}}'
        )

        with patch.object(workshop, "call_model", return_value=invalid_tool), patch.object(
            helpers, "get_weather"
        ) as weather:
            with self.assertRaises(ValueError):
                workshop.run_agent("Do something dangerous")

        weather.assert_not_called()

    def test_run_agent_rejects_malformed_model_output(self):
        with patch.object(workshop, "call_model", return_value="not JSON") as model:
            with self.assertRaises(ValueError):
                workshop.run_agent("Use a tool")

        model.assert_called_once()


if __name__ == "__main__":
    unittest.main()
