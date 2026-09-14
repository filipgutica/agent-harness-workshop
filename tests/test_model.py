import json
import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import workshop

from tests.support import FakeResponse


class CallModelTests(unittest.TestCase):
    def test_call_model_defaults_to_groq_gpt_oss_20b(self):
        response = FakeResponse({"choices": [{"message": {"content": "Hello"}}]})
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}, clear=True), patch.object(
            workshop, "urlopen", return_value=response
        ) as request:
            workshop.call_model([{"role": "user", "content": "Hello"}])

        payload = json.loads(request.call_args.args[0].data)
        self.assertEqual(payload["model"], "openai/gpt-oss-20b")
        self.assertNotIn("tools", payload)
        self.assertNotIn("response_format", payload)

    def test_call_model_returns_the_model_message(self):
        response = FakeResponse(
            {"choices": [{"message": {"content": "Hello from the model"}}]}
        )
        messages = [{"role": "user", "content": "Say hello"}]

        with patch.dict(
            os.environ,
            {"GROQ_API_KEY": "test-key", "GROQ_MODEL": "test-model"},
            clear=True,
        ), patch.object(workshop, "urlopen", return_value=response) as mocked_urlopen:
            result = workshop.call_model(messages)

        self.assertEqual(result, "Hello from the model")
        mocked_urlopen.assert_called_once()
        request = mocked_urlopen.call_args.args[0]
        timeout = mocked_urlopen.call_args.kwargs["timeout"]
        self.assertEqual(request.full_url, "https://api.groq.com/openai/v1/chat/completions")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(timeout, 30)
        self.assertEqual(
            json.loads(request.data.decode("utf-8")),
            {"model": "test-model", "messages": messages, "max_tokens": 2048},
        )

    def test_call_model_requires_an_api_key_before_making_a_request(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(
            workshop, "urlopen"
        ) as mocked_urlopen:
            with self.assertRaises(RuntimeError):
                workshop.call_model([{"role": "user", "content": "Hello"}])

        mocked_urlopen.assert_not_called()

    def test_call_model_turns_http_errors_into_runtime_errors(self):
        error = HTTPError(
            url="https://example.test/v1/chat/completions",
            code=500,
            msg="server error",
            hdrs=None,
            fp=None,
        )

        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}), patch.object(
            workshop, "urlopen", side_effect=error
        ):
            with self.assertRaisesRegex(RuntimeError, "500"):
                workshop.call_model([{"role": "user", "content": "Hello"}])


if __name__ == "__main__":
    unittest.main()
