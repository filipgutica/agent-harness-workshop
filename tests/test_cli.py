import io
import os
import re
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import Mock, call, patch

from helpers import run_cli


class CliTests(unittest.TestCase):
    def test_cli_colors_terminal_labels_and_indents_multiline_output(self):
        cases = (
            (False, {}, False),
            (True, {}, True),
            (True, {"NO_COLOR": ""}, False),
            (True, {"TERM": "dumb"}, False),
        )
        for is_terminal, environment, colored in cases:
            with self.subTest(is_terminal=is_terminal, environment=environment):
                output = io.StringIO()
                with patch("sys.argv", ["workshop.py", "--prompt", "hello"]), patch.dict(
                    os.environ, environment, clear=True
                ), patch.object(output, "isatty", return_value=is_terminal), redirect_stdout(output):
                    run_cli(lambda question: "First line\nSecond line")

                rendered = output.getvalue()
                self.assertEqual("\033[" in rendered, colored)
                plain = re.sub(r"\033\[[0-9;]*m", "", rendered)
                self.assertEqual(plain, "Output: First line\n  Second line\n")

    def test_cli_passes_the_question_to_the_application(self):
        answer = Mock(return_value="Hello from the model")
        output = io.StringIO()
        with patch("sys.argv", ["workshop.py", "--prompt", "hello workshop"]), redirect_stdout(output):
            run_cli(answer)
        answer.assert_called_once_with("hello workshop")
        self.assertEqual(output.getvalue().strip(), "Output: Hello from the model")

    def test_empty_prompt_is_rejected(self):
        answer = Mock()
        output = io.StringIO()
        with patch("sys.argv", ["workshop.py", "--prompt", ""]), redirect_stderr(output):
            with self.assertRaises(SystemExit) as error:
                run_cli(answer)
        self.assertEqual(error.exception.code, 1)
        self.assertIn("Error: Please enter a nonempty prompt.", output.getvalue())
        answer.assert_not_called()

    def test_interactive_cli_answers_questions_until_exit(self):
        for ending in ("/exit", " /QUIT ", EOFError(), KeyboardInterrupt()):
            with self.subTest(ending=ending):
                answer = Mock(side_effect=["First answer", "Second answer"])
                output = io.StringIO()
                with patch("sys.argv", ["workshop.py"]), patch(
                    "builtins.input", side_effect=["exit", "quit", ending]
                ), redirect_stdout(output):
                    run_cli(answer)

                self.assertEqual(answer.call_args_list, [call("exit"), call("quit")])
                self.assertIn("Output: First answer\nOutput: Second answer\n", output.getvalue())
                self.assertIn("Goodbye.", output.getvalue())

    def test_interactive_cli_can_retry_after_errors(self):
        for error in (None, ValueError("Invalid action"), RuntimeError("Model unavailable")):
            with self.subTest(error=error):
                answer = Mock(side_effect=[error, "Recovered"] if error else ["Recovered"])
                output = io.StringIO()
                errors = io.StringIO()
                first_question = "bad question" if error else " "
                with patch("sys.argv", ["workshop.py"]), patch(
                    "builtins.input", side_effect=[first_question, "try again", "/quit"]
                ), redirect_stdout(output), redirect_stderr(errors):
                    run_cli(answer)

                expected_calls = [call("bad question"), call("try again")] if error else [call("try again")]
                self.assertEqual(answer.call_args_list, expected_calls)
                self.assertIn(f"Error: {error or 'Please enter a nonempty prompt.'}", errors.getvalue())
                self.assertIn("Output: Recovered", output.getvalue())


if __name__ == "__main__":
    unittest.main()
