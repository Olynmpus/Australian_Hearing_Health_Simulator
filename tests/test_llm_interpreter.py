import json
import subprocess
import unittest
import math
from unittest.mock import patch, MagicMock

from src.behaviour.llm_interpreter import interpret_interaction


class TestLLMInterpreter(unittest.TestCase):

    def test_valid_response(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "interpretation": "The conversation was difficult to follow."
        })
        mock_result.stderr = ""

        with patch(
            "src.behaviour.llm_interpreter.subprocess.run",
            return_value=mock_result,
        ):
            result = interpret_interaction(
                "PERSON-001",
                {"event": "family conversation"},
            )

        self.assertEqual(result.status, "generated")
        self.assertEqual(
            result.text,
            "The conversation was difficult to follow.",
        )
        self.assertEqual(result.model, "qwen3:1.7b")
        self.assertIsNone(result.error)

    def test_timeout(self):
        with patch(
            "src.behaviour.llm_interpreter.subprocess.run",
            side_effect=subprocess.TimeoutExpired("ollama", 60),
        ):
            result = interpret_interaction(
                "PERSON-001",
                {"event": "family conversation"},
            )

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.error, "timeout")
        self.assertIsNone(result.text)

    def test_invalid_json(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "not valid json"
        mock_result.stderr = ""

        with patch(
            "src.behaviour.llm_interpreter.subprocess.run",
            return_value=mock_result,
        ):
            result = interpret_interaction(
                "PERSON-001",
                {"event": "family conversation"},
            )

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.error, "invalid_json_response")

    def test_ollama_execution_failure(self):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Model unavailable"

        with patch(
            "src.behaviour.llm_interpreter.subprocess.run",
            return_value=mock_result,
        ):
            result = interpret_interaction(
                "PERSON-001",
                {"event": "family conversation"},
            )

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.error, "Model unavailable")

    def test_invalid_agent_id_rejected(self):
        with self.assertRaises(ValueError):
            interpret_interaction(
                "",
                {"event": "family conversation"},
            )

    def test_invalid_context_rejected(self):
        with self.assertRaises(ValueError):
            interpret_interaction(
                "PERSON-001",
                "family conversation",
            )

    def test_invalid_model_rejected(self):
        with self.assertRaises(ValueError):
            interpret_interaction(
                "PERSON-001",
                {"event": "family conversation"},
                model=" ",
            )

    def test_invalid_timeout_rejected(self):
        for timeout in (0, -1, True):
            with self.subTest(timeout=timeout):
                with self.assertRaises(ValueError):
                    interpret_interaction(
                        "PERSON-001",
                        {"event": "family conversation"},
                        timeout=timeout,
                    )

    def test_invalid_response_structure(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(["unexpected", "list"])
        mock_result.stderr = ""

        with patch(
            "src.behaviour.llm_interpreter.subprocess.run",
            return_value=mock_result,
        ):
            result = interpret_interaction(
                "PERSON-001",
                {"event": "family conversation"},
            )

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.error, "invalid_response_structure")

    def test_missing_interpretation(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"other": "value"})
        mock_result.stderr = ""

        with patch(
            "src.behaviour.llm_interpreter.subprocess.run",
            return_value=mock_result,
        ):
            result = interpret_interaction(
                "PERSON-001",
                {"event": "family conversation"},
            )

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.error, "missing_interpretation")

    def test_unserializable_context(self):
        result = interpret_interaction(
            "PERSON-001",
            {"event": {"unsupported", "set"}},
        )

        self.assertEqual(result.status, "failed")
        self.assertEqual(
            result.error,
            "context_serialization_failed",
        )
        self.assertIsNone(result.text)

if __name__ == "__main__":
    unittest.main()
