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
