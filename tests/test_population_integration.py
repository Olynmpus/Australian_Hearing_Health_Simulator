import unittest

from src.agents.agent import Agent, AgentProfile
from src.population.generator import generate_population
from src.population.integration import create_hearing_support_records
from src.config_loader import load_experiment_config

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestPopulationIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.experiment = load_experiment_config(
            PROJECT_ROOT / "config" / "HH-EXP-001.json"
        )

        with open(
            PROJECT_ROOT / "config" / "population_baseline.synthetic.json",
            encoding="utf-8",
        ) as file:
            cls.distribution = json.load(file)

    def test_one_record_per_agent(self):
        agents = generate_population(
            self.experiment,
            self.distribution,
        )

        records = create_hearing_support_records(agents)

        self.assertEqual(len(records), len(agents))

    def test_agent_ids_are_preserved(self):
        agents = generate_population(
            self.experiment,
            self.distribution,
        )

        records = create_hearing_support_records(agents)

        self.assertEqual(
            [record.agent_id for record in records],
            [agent.agent_id for agent in agents],
        )
    def test_new_records_have_no_inferred_circumstances(self):
        agents = generate_population(
            self.experiment,
            self.distribution,
        )

        records = create_hearing_support_records(agents)

        for record in records:
            self.assertEqual(record.funding_arrangements, [])
            self.assertEqual(record.service_access_records, [])
            self.assertEqual(record.journeys, [])
            self.assertEqual(record.hearing_support_needs, [])
            self.assertEqual(record.service_demands, [])
            self.assertEqual(record.service_allocations, [])
            self.assertEqual(record.service_deliveries, [])

    def test_duplicate_agent_ids_are_rejected(self):
        agent = Agent(
            agent_id="PERSON-001",
            profile=AgentProfile(
                age_group="working_age_adult",
                hearing_profile="normal",
                geography="metropolitan",
            ),
        )

        with self.assertRaises(ValueError):
            create_hearing_support_records([agent, agent])

    def test_non_agent_items_are_rejected(self):
        with self.assertRaises(ValueError):
            create_hearing_support_records(["not an agent"])

    def test_non_list_input_is_rejected(self):
        with self.assertRaises(ValueError):
            create_hearing_support_records(None)

    def test_empty_population_returns_empty_records(self):
        self.assertEqual(create_hearing_support_records([]), [])


if __name__ == "__main__":
    unittest.main()
