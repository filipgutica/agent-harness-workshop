"""Small test fixtures shared by the workshop stages."""

import json


class FakeResponse:
    """A tiny response object with the part of urlopen's interface we use."""

    def __init__(self, body: dict):
        self._body = json.dumps(body).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self._body


def weather_response():
    return {
        "timezone": "America/Vancouver",
        "current": {
            "time": "2026-09-13T12:00",
            "temperature_2m": 14.5,
            "apparent_temperature": 13.1,
            "precipitation": 0.0,
        },
        "current_units": {
            "time": "iso8601",
            "temperature_2m": "°C",
            "apparent_temperature": "°C",
            "precipitation": "mm",
        },
    }


def geocoding_response():
    return {"results": [{
        "name": "Vancouver",
        "admin1": "British Columbia",
        "country": "Canada",
        "latitude": 49.2827,
        "longitude": -123.1207,
    }]}


def native_tool_call(*, call_id="call_weather", name="get_weather", arguments='{"location":"Vancouver"}'):
    """A wire-format fixture, with arguments serialized exactly as the API returns them."""
    return {"id": call_id, "type": "function", "function": {"name": name, "arguments": arguments}}
