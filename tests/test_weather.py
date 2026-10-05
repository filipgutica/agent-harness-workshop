import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse

import helpers as workshop

from tests.support import FakeResponse, geocoding_response, weather_response


class WeatherToolTests(unittest.TestCase):
    def test_get_weather_returns_the_current_weather_data(self):
        cities = (
            (" vAnCoUvEr ", "Vancouver", "British Columbia", "Canada", 49.2827, -123.1207, "America/Vancouver"),
            ("Toronto", "Toronto", "Ontario", "Canada", 43.70011, -79.4163, "America/Toronto"),
            ("Paris, France", "Paris", "Île-de-France", "France", 48.85341, 2.3488, "Europe/Paris"),
            ("Tokyo", "Tokyo", "Tokyo", "Japan", 35.6895, 139.69171, "Asia/Tokyo"),
        )
        for requested, name, region, country, latitude, longitude, timezone in cities:
            with self.subTest(city=requested):
                match = {"results": [{
                    "name": name, "admin1": region, "country": country,
                    "latitude": latitude, "longitude": longitude,
                }]}
                forecast = weather_response()
                forecast["timezone"] = timezone
                output = io.StringIO()
                with patch.object(workshop, "urlopen", side_effect=[
                    FakeResponse(match), FakeResponse(forecast),
                ]) as http, redirect_stdout(output):
                    result = workshop.get_weather(location=requested)

                self.assertEqual(result["location"], f"{name}, {region}, {country}")
                self.assertEqual(result["source"], "Open-Meteo")
                self.assertEqual(result["timezone"], timezone)
                self.assertEqual(result["current"], forecast["current"])
                self.assertEqual(result["units"], forecast["current_units"])
                self.assertEqual(http.call_count, 2)
                lookup, weather = [call.args[0] for call in http.call_args_list]
                self.assertEqual(lookup.get_method(), "GET")
                self.assertEqual(weather.get_method(), "GET")
                self.assertEqual(lookup.full_url.split("?", 1)[0], "https://geocoding-api.open-meteo.com/v1/search")
                self.assertEqual(weather.full_url.split("?", 1)[0], "https://api.open-meteo.com/v1/forecast")
                self.assertEqual(parse_qs(urlparse(lookup.full_url).query)["name"], [requested.strip()])
                query = parse_qs(urlparse(weather.full_url).query)
                self.assertEqual(query["latitude"], [str(latitude)])
                self.assertEqual(query["longitude"], [str(longitude)])
                self.assertEqual(query["current"], ["temperature_2m,apparent_temperature,precipitation"])
                self.assertEqual(query["timezone"], ["auto"])
                self.assertTrue(all(call.kwargs["timeout"] == 30 for call in http.call_args_list))
                trace = output.getvalue()
                self.assertIn("get_weather: GET https://geocoding-api.open-meteo.com/v1/search", trace)
                self.assertIn(
                    f"get_weather: GET https://api.open-meteo.com/v1/forecast (current weather for {name}, {region}, {country}).",
                    trace,
                )

    def test_get_weather_rejects_unknown_locations(self):
        for body in ({}, {"results": []}):
            with self.subTest(body=body), patch.object(
                workshop, "urlopen", return_value=FakeResponse(body)
            ) as http:
                with self.assertRaisesRegex(ValueError, "No city found"):
                    workshop.get_weather(location="NotARealCity")
                http.assert_called_once()

    def test_get_weather_rejects_invalid_locations_before_http(self):
        for location in ("", "  ", None, 123):
            with self.subTest(location=location), patch.object(workshop, "urlopen") as http:
                with self.assertRaises(ValueError):
                    workshop.get_weather(location=location)
                http.assert_not_called()

    def test_get_weather_rejects_incomplete_api_data(self):
        invalid_matches = (
            {"results": "invalid"}, {"results": [None]},
            {"results": [{"name": "Vancouver"}]},
            {"results": [{"name": "", "latitude": 49, "longitude": -123}]},
            {"results": [{"name": "Vancouver", "latitude": True, "longitude": -123}]},
            {"results": [{"name": "Vancouver", "latitude": 91, "longitude": -123}]},
        )
        for body in invalid_matches:
            with self.subTest(body=body), patch.object(
                workshop, "urlopen", return_value=FakeResponse(body)
            ) as http:
                with self.assertRaises(RuntimeError):
                    workshop.get_weather(location="Vancouver")
                http.assert_called_once()
        for field in ("current", "current_units", "timezone", "precipitation"):
            body = weather_response()
            if field == "precipitation":
                del body["current"][field]
            else:
                del body[field]
            with self.subTest(field=field), patch.object(workshop, "urlopen", side_effect=[
                FakeResponse(geocoding_response()), FakeResponse(body),
            ]):
                with self.assertRaises(RuntimeError):
                    workshop.get_weather(location="Vancouver")

    def test_get_weather_reports_api_failures_without_another_request(self):
        for phase in ("Geocoding", "Weather"):
            for failure in ("http", "network", "timeout", "json"):
                if failure == "http":
                    response = HTTPError("https://example.test", 503, "Unavailable", {}, None)
                elif failure == "network":
                    response = URLError("Unavailable")
                elif failure == "timeout":
                    response = TimeoutError()
                else:
                    response = io.BytesIO(b"not JSON")
                replies = [response] if phase == "Geocoding" else [FakeResponse(geocoding_response()), response]
                with self.subTest(phase=phase, failure=failure), patch.object(
                    workshop, "urlopen", side_effect=replies
                ) as http:
                    with self.assertRaisesRegex(RuntimeError, phase + " API"):
                        workshop.get_weather(location="Vancouver")
                    self.assertEqual(http.call_count, len(replies))

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
