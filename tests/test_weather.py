import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import helpers as workshop

from tests.support import FakeResponse, weather_response


class WeatherToolTests(unittest.TestCase):
    def test_get_weather_returns_the_current_weather_data(self):
        with patch.object(
            workshop, "urlopen", return_value=FakeResponse(weather_response())
        ) as mocked_urlopen:
            result = workshop.get_weather(location=" vAnCoUvEr ")

        self.assertEqual(result["location"], "Vancouver")
        self.assertEqual(result["source"], "Open-Meteo")
        self.assertEqual(result["current"], weather_response()["current"])
        self.assertEqual(result["units"], weather_response()["current_units"])
        mocked_urlopen.assert_called_once()
        request = mocked_urlopen.call_args.args[0]
        timeout = mocked_urlopen.call_args.kwargs["timeout"]
        query = parse_qs(urlparse(request.full_url).query)
        self.assertEqual(query["latitude"], ["49.2827"])
        self.assertEqual(query["longitude"], ["-123.1207"])
        self.assertEqual(
            query["current"], ["temperature_2m,apparent_temperature,precipitation"]
        )
        self.assertEqual(query["timezone"], ["America/Vancouver"])
        self.assertEqual(timeout, 30)

    def test_get_weather_rejects_unknown_locations(self):
        with patch.object(workshop, "urlopen") as mocked_urlopen:
            with self.assertRaises(ValueError):
                workshop.get_weather(location="Toronto")

        mocked_urlopen.assert_not_called()

    def test_get_weather_rejects_incomplete_api_data(self):
        response = weather_response()
        del response["current"]["precipitation"]

        with patch.object(workshop, "urlopen", return_value=FakeResponse(response)):
            with self.assertRaises(RuntimeError):
                workshop.get_weather(location="Vancouver")

    def test_dispatch_tool_calls_the_allowed_tool(self):
        expected = {"location": "Vancouver", "source": "test"}

        with patch.object(workshop, "get_weather", return_value=expected) as weather:
            result = workshop.dispatch_tool(
                {
                    "action": "tool-call",
                    "tool": "get_weather",
                    "parameters": {"location": "Vancouver"},
                }
            )

        self.assertEqual(result, expected)
        weather.assert_called_once_with(location="Vancouver")

    def test_dispatch_tool_rejects_unknown_tools_and_bad_parameters(self):
        invalid_actions = [
            {
                "action": "tool-call",
                "tool": "send_email",
                "parameters": {"location": "Vancouver"},
            },
            {
                "action": "tool-call",
                "tool": "get_weather",
                "parameters": {"location": 123},
            },
            {
                "action": "tool-call",
                "tool": "get_weather",
                "parameters": {"location": "Vancouver", "extra": True},
            },
        ]

        with patch.object(workshop, "get_weather") as weather:
            for action in invalid_actions:
                with self.subTest(action=action), self.assertRaises(ValueError):
                    workshop.dispatch_tool(action)

        weather.assert_not_called()


if __name__ == "__main__":
    unittest.main()
