import json
import unittest

from helpers import parse_answer


class ParseAnswerTests(unittest.TestCase):
    def test_parses_a_final_json_answer(self):
        self.assertEqual(parse_answer('{"answer":"The answer is 42."}'), {"answer": "The answer is 42."})

    def test_rejects_invalid_json_and_answer_shapes(self):
        cases = ["not JSON", '```json\n{"answer":"ok"}\n```']
        cases += [json.dumps(value) for value in [[], {}, {"answer": ""}, {"answer": " "},
                 {"answer": 42}, {"answer": "ok", "extra": True}]]
        for raw in cases:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_answer(raw)


if __name__ == "__main__":
    unittest.main()
