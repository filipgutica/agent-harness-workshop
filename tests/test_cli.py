import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class EchoCliTests(unittest.TestCase):
    def run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, "workshop.py", *arguments],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    def test_echo_mode_prints_the_prompt(self):
        result = self.run_cli("--mode", "echo", "--prompt", "hello workshop")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "Echo: hello workshop")
        self.assertEqual(result.stderr, "")

    def test_empty_prompt_is_rejected(self):
        result = self.run_cli("--mode", "echo", "--prompt", "")

        self.assertEqual(result.returncode, 1)
        self.assertIn("Error: Please enter a nonempty prompt.", result.stderr)


if __name__ == "__main__":
    unittest.main()
