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
            self.assertEqual(len(history), 4)
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
                relationships["FRIEND-001"].perceived_support,
                0.60
            )

            self.assertAlmostEqual(
                relationships["SERVICE-001"].trust,
                0.40
            )

            self.assertTrue(database.exists())


if __name__ == "__main__":
    unittest.main()
