import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from src.simulation.longitudinal_demo import run_experiment
from src.behaviour.llm_interpreter import InterpretationResult


class TestLongitudinalDemo(unittest.TestCase):

    def test_four_month_experiment(self):

        with tempfile.TemporaryDirectory() as folder:

            database = Path(folder) / "experiment.db"

            person, relationships, history, snapshots = (
                run_experiment(database)
            )

            self.assertEqual(person.current_month, 4)
            self.assertEqual(set(history.keys()), {
                "PERSON-001",
                "FAMILY-001",
                "FRIEND-001",
                "SERVICE-001",
            })

            self.assertEqual(len(history["PERSON-001"]), 4)
            self.assertEqual(len(history["FAMILY-001"]), 1)
            self.assertEqual(len(history["FRIEND-001"]), 1)
            self.assertEqual(len(history["SERVICE-001"]), 2)

            person_event = history["PERSON-001"][0]
            family_event = history["FAMILY-001"][0]

            person_communication = (
                person_event["additional_details"]["communication_event"]
            )

            family_communication = (
                family_event["additional_details"]["communication_event"]
            )

            self.assertEqual(person_communication["channel"], "speech")
            self.assertEqual(
                person_communication["initial_outcome"],
                "not_assessed",
            )
            self.assertEqual(
                person_communication["final_outcome"],
                "not_assessed",
            )
            self.assertEqual(person_communication, family_communication)

            self.assertNotEqual(
                person_event["agent_interpretation"],
                family_event["agent_interpretation"],
            )

            person_llm = (
                person_event["additional_details"]["llm_interpretation"]
            )
            family_llm = (
                family_event["additional_details"]["llm_interpretation"]
            )

            self.assertEqual(person_llm["source"], "local_llm")
            self.assertEqual(person_llm["status"], "not_generated")
            self.assertIsNone(person_llm["text"])
            self.assertIsNone(person_llm["model"])
            self.assertFalse(person_llm["verified"])

            self.assertEqual(family_llm["source"], "local_llm")
            self.assertEqual(family_llm["status"], "not_generated")
            self.assertIsNone(family_llm["text"])
            self.assertFalse(family_llm["verified"])

            self.assertEqual(len(snapshots), 4)

            self.assertAlmostEqual(
                person.state.communication_confidence,
                0.50
            )
            self.assertAlmostEqual(
                person.state.social_participation,
                0.52
            )
            self.assertAlmostEqual(
                person.state.trust_in_services,
                0.35
            )
            self.assertAlmostEqual(
                person.state.frustration,
                0.25
            )

            self.assertAlmostEqual(
                relationships["PERSON-001"]["FRIEND-001"].perceived_support,
                0.60
            )
            self.assertAlmostEqual(
                relationships["PERSON-001"]["SERVICE-001"].trust,
                0.40
            )

            self.assertTrue(database.exists())

    @patch("src.simulation.longitudinal_demo.interpret_interaction")
    def test_llm_generates_independent_interpretations(self, mock_interpret):

        mock_interpret.side_effect = [
            InterpretationResult(
                text="The participant may have experienced difficulty.",
                model="qwen3:1.7b",
                status="generated",
            ),
            InterpretationResult(
                text="The family participant's interpretation is unknown.",
                model="qwen3:1.7b",
                status="generated",
            ),
        ]

        with tempfile.TemporaryDirectory() as folder:

            database = Path(folder) / "experiment.db"

            person, relationships, history, snapshots = (
                run_experiment(database, enable_llm=True)
            )

            self.assertEqual(mock_interpret.call_count, 2)

            first_call = mock_interpret.call_args_list[0]
            second_call = mock_interpret.call_args_list[1]

            self.assertEqual(
                first_call.kwargs["agent_id"],
                "PERSON-001",
            )
            self.assertEqual(
                second_call.kwargs["agent_id"],
                "FAMILY-001",
            )
            first_context = first_call.kwargs["interaction_context"]
            second_context = second_call.kwargs["interaction_context"]

            self.assertNotEqual(
                first_context["current_interaction"]["participant_role"],
                second_context["current_interaction"]["participant_role"],
            )

            self.assertEqual(
                first_context["current_interaction"]["event_description"],
                second_context["current_interaction"]["event_description"],
            )

            self.assertEqual(
                first_context["individual"]["agent_id"],
                "PERSON-001",
            )

            self.assertEqual(
                second_context["individual"]["agent_id"],
                "FAMILY-001",
            )

            person_llm = (
                history["PERSON-001"][0]["additional_details"]["llm_interpretation"]
            )
            family_llm = (
                history["FAMILY-001"][0]["additional_details"]["llm_interpretation"]
            )

            self.assertEqual(
                person_llm["text"],
                "The participant may have experienced difficulty.",
            )
            self.assertEqual(
                family_llm["text"],
                "The family participant's interpretation is unknown.",
            )

            self.assertFalse(person_llm["verified"])
            self.assertFalse(family_llm["verified"])

            self.assertEqual(
                history["PERSON-001"][0]["outcome"],
                "negative_communication",
            )

    @patch("src.simulation.longitudinal_demo.interpret_interaction")
    def test_llm_failure_does_not_interrupt_simulation(self, mock_interpret):

        mock_interpret.side_effect = RuntimeError("Ollama unavailable")

        with tempfile.TemporaryDirectory() as folder:

            database = Path(folder) / "experiment.db"

            person, relationships, history, snapshots = (
                run_experiment(database, enable_llm=True)
            )

            self.assertEqual(mock_interpret.call_count, 2)

            person_llm = (
                history["PERSON-001"][0]["additional_details"]["llm_interpretation"]
            )

            family_llm = (
                history["FAMILY-001"][0]["additional_details"]["llm_interpretation"]
            )

            self.assertEqual(person_llm["status"], "failed")
            self.assertEqual(family_llm["status"], "failed")

            self.assertIsNone(person_llm["text"])
            self.assertIsNone(family_llm["text"])

            self.assertEqual(
                history["PERSON-001"][0]["outcome"],
                "negative_communication",
            )

            self.assertEqual(person.current_month, 4)
            self.assertEqual(len(snapshots), 4)

if __name__ == "__main__":
    unittest.main()
