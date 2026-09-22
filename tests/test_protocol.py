import json
import unittest

import helpers as workshop


class ParseActionTests(unittest.TestCase):
    def test_parses_a_final_response(self):
        raw = '{"action":"response","content":"The answer is 42."}'

        self.assertEqual(
            workshop.parse_action(raw),
            {"action": "response", "content": "The answer is 42."},
        )

    def test_parses_a_tool_call(self):
        raw = (
            '{"action":"tool-call","tool":"get_weather",'
            '"parameters":{"location":"Vancouver"}}'
        )

        self.assertEqual(
            workshop.parse_action(raw),
            {
                "action": "tool-call",
                "tool": "get_weather",
                "parameters": {"location": "Vancouver"},
            },
        )

    def test_rejects_malformed_json(self):
        with self.assertRaises(ValueError):
            workshop.parse_action("this is not JSON")

    def test_rejects_invalid_response_shapes(self):
        invalid_values = [
            {"action": "response", "content": ""},
            {"action": "response", "content": 123},
            {"action": "response", "content": "ok", "extra": True},
            {"action": "tool-call", "tool": "", "parameters": {}},
            {"action": "tool-call", "tool": "get_weather", "parameters": []},
            {"action": "tool-call", "tool": "get_weather"},
            {"action": "unknown", "content": "maybe"},
        ]

        for value in invalid_values:
            with self.subTest(value=value), self.assertRaises(ValueError):
                workshop.parse_action(json.dumps(value))


if __name__ == "__main__":
    unittest.main()
