import unittest
from pathlib import Path

from src.simulation.population_experiment import (
    run_population_experiment,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestPopulationExperiment(unittest.TestCase):

    def setUp(self):
        self.experiment = run_population_experiment(
            PROJECT_ROOT / "config" / "HH-EXP-001.json",
            PROJECT_ROOT / "config" / "population_baseline.synthetic.json",
        )

    def test_population_size_matches_configuration(self):
        self.assertEqual(self.experiment.population_size, 1000)

    def test_one_support_record_per_agent(self):
        self.assertEqual(
            len(self.experiment.support_records),
            len(self.experiment.agents),
        )

    def test_agent_identifiers_are_unique(self):
        identifiers = [
            agent.agent_id for agent in self.experiment.agents
        ]
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_support_records_preserve_agent_identifiers(self):
        agent_ids = [
            agent.agent_id for agent in self.experiment.agents
        ]
        record_ids = [
            record.agent_id for record in self.experiment.support_records
        ]
        self.assertEqual(agent_ids, record_ids)

    def test_experiment_metadata(self):
        self.assertEqual(self.experiment.experiment_id, "HH-EXP-001")
        self.assertEqual(self.experiment.duration_months, 12)
        self.assertEqual(self.experiment.random_seed, 42)
        self.assertEqual(
            self.experiment.evidence_status,
            "simulation_assumption",
        )

    def test_summary_reports_population_counts(self):
        summary = self.experiment.summary()

        self.assertEqual(summary["agent_count"], 1000)
        self.assertEqual(summary["support_record_count"], 1000)

    def test_summary_contains_all_population_distributions(self):
        summary = self.experiment.summary()

        distributions = summary["population_distributions"]

        self.assertEqual(
            set(distributions.keys()),
            {
                "age_group",
                "hearing_profile",
                "geography",
                "functional_status",
            },
        )

    def test_functional_status_distribution_totals_population(self):
        summary = self.experiment.summary()

        distribution = summary["population_distributions"][
            "functional_status"
        ]

        total = sum(
            item["count"] for item in distribution.values()
        )

        self.assertEqual(total, self.experiment.population_size)
        self.assertAlmostEqual(
            sum(item["percentage"] for item in distribution.values()),
            100.0,
            places=1,
        )

if __name__ == "__main__":
    unittest.main()
