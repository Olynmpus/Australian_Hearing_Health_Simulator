import tempfile
import unittest

from pathlib import Path

from src.simulation.longitudinal_demo import run_experiment


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

            self.assertEqual(
                person_communication["channel"],
                "speech",
            )

            self.assertEqual(
                person_communication["initial_outcome"],
                "not_assessed",
            )

            self.assertEqual(
                person_communication["final_outcome"],
                "not_assessed",
            )

            self.assertEqual(
                person_communication,
                family_communication,
            )

            self.assertNotEqual(
                person_event["agent_interpretation"],
                family_event["agent_interpretation"],
            )

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


if __name__ == "__main__":
    unittest.main()
