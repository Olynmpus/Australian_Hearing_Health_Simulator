import tempfile
import unittest

from pathlib import Path

from src.agents.memory_store import MemoryStore


class TestMemoryStore(unittest.TestCase):

    def test_record_and_retrieve_event(self):

        with tempfile.TemporaryDirectory() as temporary_folder:

            database = Path(temporary_folder) / "test_memory.db"
            memory = MemoryStore(database)

            memory.record_event(
                agent_id="PERSON-001",
                month=1,
                event_type="family_conversation",
                sender_id="FAMILY-001",
                recipient_id="PERSON-001",
                actual_message="I already told you.",
                agent_interpretation="My family is frustrated with me.",
                outcome="negative_communication",
                source_accuracy=None,
                emotional_appraisal="embarrassment"
            )

            history = memory.get_history("PERSON-001")

            self.assertEqual(len(history), 1)
            self.assertEqual(
                history[0]["actual_message"],
                "I already told you."
            )
            self.assertEqual(
                history[0]["agent_interpretation"],
                "My family is frustrated with me."
            )

    def test_history_survives_reopening_database(self):

        with tempfile.TemporaryDirectory() as temporary_folder:

            database = Path(temporary_folder) / "test_memory.db"

            first_memory = MemoryStore(database)

            first_memory.record_event(
                agent_id="PERSON-002",
                month=2,
                event_type="service_interaction",
                outcome="misdirected_information",
                actual_message="You need to contact another service."
            )

            second_memory = MemoryStore(database)
            history = second_memory.get_history("PERSON-002")

            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]["month"], 2)

    def test_invalid_accuracy_is_rejected(self):

        with tempfile.TemporaryDirectory() as temporary_folder:

            memory = MemoryStore(
                Path(temporary_folder) / "test_memory.db"
            )

            with self.assertRaises(ValueError):
                memory.record_event(
                    agent_id="PERSON-003",
                    month=1,
                    event_type="information",
                    outcome="unknown",
                    source_accuracy=1.5
                )
    def test_interpretation_provenance_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary_folder:

            database = Path(temporary_folder) / "test_memory.db"
            memory = MemoryStore(database)

            provenance = {
                "source": "scenario_script",
                "evidence_status": "simulation_assumption",
                "verified": False,
            }

            memory.record_event(
                agent_id="PERSON-001",
                month=1,
                event_type="family_conversation",
                outcome="negative_communication",
                agent_interpretation="I felt excluded.",
                additional_details={
                    "interpretation_provenance": provenance,
                },
            )

            history = memory.get_history("PERSON-001")

            self.assertEqual(
                history[0]["additional_details"]["interpretation_provenance"],
                provenance,
            )
    def test_same_interaction_can_have_individual_perspectives(self):

        with tempfile.TemporaryDirectory() as temporary_folder:

            database = Path(temporary_folder) / "test_memory.db"
            memory = MemoryStore(database)

            interaction_id = "INTERACTION-001"

            memory.record_event(
                agent_id="PERSON-001",
                month=1,
                event_type="family_conversation",
                sender_id="FAMILY-001",
                recipient_id="PERSON-001",
                actual_message="A difficult family conversation.",
                agent_interpretation="I felt excluded.",
                outcome="negative_communication",
                additional_details={
                    "interaction_id": interaction_id,
                    "perspective": "recipient",
                },
            )

            memory.record_event(
                agent_id="FAMILY-001",
                month=1,
                event_type="family_conversation",
                sender_id="PERSON-001",
                recipient_id="FAMILY-001",
                actual_message="A difficult family conversation.",
                agent_interpretation="I thought the conversation was becoming frustrating.",
                outcome="negative_communication",
                additional_details={
                    "interaction_id": interaction_id,
                    "perspective": "recipient",
                },
            )

            person_history = memory.get_history("PERSON-001")
            family_history = memory.get_history("FAMILY-001")

            self.assertEqual(len(person_history), 1)
            self.assertEqual(len(family_history), 1)

            self.assertEqual(
                person_history[0]["additional_details"]["interaction_id"],
                family_history[0]["additional_details"]["interaction_id"],
            )

            self.assertNotEqual(
                person_history[0]["agent_interpretation"],
                family_history[0]["agent_interpretation"],
            )
if __name__ == "__main__":
    unittest.main()
