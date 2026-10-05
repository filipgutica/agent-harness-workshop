import json
import io
import os
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from urllib.error import HTTPError

import helpers as workshop

from tests.support import FakeResponse, native_tool_call


class CallModelTests(unittest.TestCase):
    def test_call_model_traces_the_follow_up_conversation_and_reply(self):
        tool_result = '{"temperature":16.5}'
        history = [
            {"role": "system", "content": "Use the provided data."},
            {"role": "user", "content": "Weather?"},
            {"role": "assistant", "content": None, "tool_calls": [native_tool_call()]},
            {"role": "tool", "tool_call_id": "call_weather", "content": tool_result},
        ]
        cases = (
            (history[:2], "[SYSTEM_PROMPT] + [USER_MESSAGE]", "Weather?"),
            (history, "[SYSTEM_PROMPT] + [USER_MESSAGE] + [ASSISTANT_MESSAGE] + [TOOL_MESSAGE]", tool_result),
        )
        for messages, labels, latest_content in cases:
            with self.subTest(message_count=len(messages)):
                output = io.StringIO()

                def respond(request, *, timeout):
                    print("HTTP request sent")
                    self.assertEqual(json.loads(request.data)["messages"], messages)
                    return FakeResponse({"choices": [{"message": {"role": "assistant", "content": "It is 16.5 C."}}]})

                with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}, clear=True), patch.object(
                    workshop, "urlopen", side_effect=respond
                ), redirect_stdout(output):
                    result = workshop.call_model(messages)

                trace = output.getvalue()
                self.assertEqual(result, {"role": "assistant", "content": "It is 16.5 C."})
                self.assertIn(f"sending {labels} to openai/gpt-oss-120b ({len(messages)} messages).", trace)
                latest_role = "TOOL_MESSAGE" if len(messages) == 4 else "USER_MESSAGE"
                self.assertIn(f"Model input (latest message): [{latest_role}]\n    " + latest_content, trace)
                self.assertLess(trace.index("waiting for the model reply"), trace.index("HTTP request sent"))
                self.assertLess(trace.index("HTTP request sent"), trace.index("received the model reply"))
                self.assertNotIn("test-key", trace)

    def test_call_model_defaults_to_groq_gpt_oss_120b(self):
        response = FakeResponse({"choices": [{"message": {"role": "assistant", "content": "Hello"}}]})
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}, clear=True), patch.object(
            workshop, "urlopen", return_value=response
        ) as request:
            workshop.call_model([{"role": "user", "content": "Hello"}])

        payload = json.loads(request.call_args.args[0].data)
        self.assertEqual(payload["model"], "openai/gpt-oss-120b")
        self.assertNotIn("tools", payload)
        self.assertNotIn("response_format", payload)

    def test_call_model_returns_the_model_message(self):
        messages = [{"role": "user", "content": "Say hello"}]
        schema_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "greeting",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {"greeting": {"type": "string"}},
                    "required": ["greeting"],
                    "additionalProperties": False,
                },
            },
        }

        for response_format in (None, {"type": "json_object"}, schema_format):
            with self.subTest(response_format=response_format):
                content = "Hello from the model" if response_format is None else '{"greeting":"Hello"}'
                response = FakeResponse({"choices": [{"message": {"role": "assistant", "content": content, "tool_calls": []}}]})
                with patch.dict(
                    os.environ,
                    {"GROQ_API_KEY": "test-key", "GROQ_MODEL": "test-model"},
                    clear=True,
                ), patch.object(workshop, "urlopen", return_value=response) as mocked_urlopen:
                    if response_format is None:
                        result = workshop.call_model(messages)
                    else:
                        result = workshop.call_model(messages, response_format=response_format)

                self.assertEqual(result, {"role": "assistant", "content": content})
                mocked_urlopen.assert_called_once()
                request = mocked_urlopen.call_args.args[0]
                timeout = mocked_urlopen.call_args.kwargs["timeout"]
                self.assertEqual(request.full_url, "https://api.groq.com/openai/v1/chat/completions")
                self.assertEqual(request.get_method(), "POST")
                self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
                self.assertEqual(request.get_header("Content-type"), "application/json")
                user_agent = request.get_header("User-agent", "")
                self.assertTrue(user_agent.strip())
                self.assertFalse(user_agent.startswith("Python-urllib"))
                self.assertEqual(timeout, 30)
                expected_payload = {"model": "test-model", "messages": messages, "max_tokens": 2048}
                if response_format is not None:
                    expected_payload["response_format"] = response_format
                self.assertEqual(json.loads(request.data.decode("utf-8")), expected_payload)

    def test_native_tool_calls_survive_transport_with_null_content(self):
        tools = [{"type": "function", "function": {"name": "get_weather", "parameters": {"type": "object"}}}]
        native = {"role": "assistant", "content": None, "tool_calls": [native_tool_call()]}
        response = FakeResponse({"choices": [{"message": {**native, "reasoning": "server-only metadata"}}]})
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}, clear=True), patch.object(
            workshop, "urlopen", return_value=response
        ) as http:
            result = workshop.call_model([{"role": "user", "content": "Weather?"}], tools=tools)
        self.assertEqual(result, native)
        self.assertEqual(json.loads(http.call_args.args[0].data)["tools"], tools)

    def test_call_model_rejects_invalid_envelopes_and_truncation(self):
        cases = [
            ({"role": "user", "content": "wrong role"}, "stop"),
            ({"role": "assistant", "content": ""}, "stop"),
            ({"role": "assistant", "content": 123}, "stop"),
            ({"role": "assistant", "content": "partial"}, "length"),
            ({"role": "assistant", "tool_calls": []}, "tool_calls"),
            ({"role": "assistant", "tool_calls": [native_tool_call(call_id="")]}, "tool_calls"),
            ({"role": "assistant", "tool_calls": [native_tool_call(arguments={})]}, "tool_calls"),
            ({"role": "assistant", "tool_calls": [native_tool_call(), native_tool_call()]}, "tool_calls"),
        ]
        for message, finish_reason in cases:
            with self.subTest(message=message), patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}), patch.object(
                workshop, "urlopen", return_value=FakeResponse({"choices": [{"message": message, "finish_reason": finish_reason}]})
            ):
                with self.assertRaises(RuntimeError):
                    workshop.call_model([{"role": "user", "content": "Weather?"}], tools=[{}])

    def test_schema_formatting_does_not_combine_with_tools(self):
        with patch.object(workshop, "urlopen") as http, self.assertRaisesRegex(ValueError, "separate request"):
            workshop.call_model([], tools=[{}], response_format={"type": "json_schema"})
        http.assert_not_called()

    def test_call_model_requires_an_api_key_before_making_a_request(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(
            workshop, "urlopen"
        ) as mocked_urlopen:
            with self.assertRaises(RuntimeError):
                workshop.call_model([{"role": "user", "content": "Hello"}])

        mocked_urlopen.assert_not_called()

    def test_call_model_turns_http_errors_into_runtime_errors(self):
        for status, explanation in (
            (400, "request format and model compatibility"),
            (500, "key, model, and quota"),
        ):
            with self.subTest(status=status):
                error = HTTPError(
                    url="https://example.test/v1/chat/completions",
                    code=status,
                    msg="request failed",
                    hdrs=None,
                    fp=None,
                )
                with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}), patch.object(
                    workshop, "urlopen", side_effect=error
                ):
                    with self.assertRaisesRegex(RuntimeError, f"HTTP {status}.*{explanation}"):
                        workshop.call_model([{"role": "user", "content": "Hello"}])


if __name__ == "__main__":
    unittest.main()
