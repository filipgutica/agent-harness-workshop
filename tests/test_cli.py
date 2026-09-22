import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import Mock, patch

from helpers import run_cli


class CliTests(unittest.TestCase):
    def test_cli_passes_the_question_to_the_application(self):
        answer = Mock(return_value="Hello from the model")
        output = io.StringIO()
        with patch("sys.argv", ["workshop.py", "--prompt", "hello workshop"]), redirect_stdout(output):
            run_cli(answer)
        answer.assert_called_once_with("hello workshop")
        self.assertEqual(output.getvalue().strip(), "Assistant: Hello from the model")

    def test_empty_prompt_is_rejected(self):
        answer = Mock()
        output = io.StringIO()
        with patch("sys.argv", ["workshop.py", "--prompt", ""]), redirect_stderr(output):
            with self.assertRaises(SystemExit) as error:
                run_cli(answer)
        self.assertEqual(error.exception.code, 1)
        self.assertIn("Error: Please enter a nonempty prompt.", output.getvalue())
        answer.assert_not_called()


if __name__ == "__main__":
    unittest.main()
