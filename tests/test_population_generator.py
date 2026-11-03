import json
import unittest

from pathlib import Path

from src.config_loader import load_experiment_config
from src.population.generator import generate_population


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestPopulationGenerator(unittest.TestCase):

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

    def test_generates_configured_population_size(self):
        agents = generate_population(
            self.experiment,
            self.distribution,
        )

        self.assertEqual(len(agents), 1000)

    def test_agent_identifiers_are_unique(self):
        agents = generate_population(
            self.experiment,
            self.distribution,
        )

        identifiers = [agent.agent_id for agent in agents]

        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_same_seed_produces_same_population(self):
        first = generate_population(
            self.experiment,
            self.distribution,
        )

        second = generate_population(
            self.experiment,
            self.distribution,
        )

        first_profiles = [
            (
                agent.profile.age_group,
                agent.profile.hearing_profile,
                agent.profile.geography,
                agent.profile.onset_type,
                agent.profile.progression_type,
            )
            for agent in first
        ]

        second_profiles = [
            (
                agent.profile.age_group,
                agent.profile.hearing_profile,
                agent.profile.geography,
                agent.profile.onset_type,
                agent.profile.progression_type,
            )
            for agent in second
        ]

        self.assertEqual(first_profiles, second_profiles)

    def test_generated_agents_pass_validation(self):
        agents = generate_population(
            self.experiment,
            self.distribution,
        )

        for agent in agents:
            self.assertTrue(agent.validate())

    def test_communication_preferences_are_not_inferred(self):
        agents = generate_population(
            self.experiment,
            self.distribution,
        )

        for agent in agents:
            self.assertEqual(
                agent.profile.communication_profile.modalities,
                [],
            )

    def test_invalid_weight_is_rejected(self):
        distribution = json.loads(json.dumps(self.distribution))
        distribution["weights"]["hearing_profiles"]["normal"] = -1

        with self.assertRaises(ValueError):
            generate_population(self.experiment, distribution)

    def test_missing_weight_is_rejected(self):
        distribution = json.loads(json.dumps(self.distribution))
        del distribution["weights"]["age_groups"]["infant"]

        with self.assertRaises(ValueError):
            generate_population(self.experiment, distribution)

    def test_unlabelled_distribution_is_rejected(self):
        distribution = json.loads(json.dumps(self.distribution))
        distribution["evidence_status"] = "unknown"

        with self.assertRaises(ValueError):
            generate_population(self.experiment, distribution)
    def test_normal_audiometry_can_have_reported_difficulty(self):
        experiment = json.loads(json.dumps(self.experiment))
        distribution = json.loads(json.dumps(self.distribution))

        experiment["population"]["size"] = 1

        distribution["weights"]["hearing_profiles"] = {
            "normal": 1,
            "mild": 0,
            "moderate": 0,
            "severe": 0,
            "profound": 0,
        }

        distribution["weights"]["auditory_functional_status"] = {
            "no_identified_difficulty": 0,
            "difficulty_reported": 1,
            "functional_difficulty_confirmed": 0,
            "unknown": 0,
        }

        agents = generate_population(experiment, distribution)

        self.assertEqual(agents[0].profile.hearing_profile, "normal")
        self.assertEqual(
            agents[0].profile.auditory_functional_status,
            "difficulty_reported",
        )

    def test_normal_audiometry_can_have_confirmed_functional_difficulty(self):
        experiment = json.loads(json.dumps(self.experiment))
        distribution = json.loads(json.dumps(self.distribution))

        experiment["population"]["size"] = 1

        distribution["weights"]["hearing_profiles"] = {
            "normal": 1,
            "mild": 0,
            "moderate": 0,
            "severe": 0,
            "profound": 0,
        }

        distribution["weights"]["auditory_functional_status"] = {
            "no_identified_difficulty": 0,
            "difficulty_reported": 0,
            "functional_difficulty_confirmed": 1,
            "unknown": 0,
        }

        agents = generate_population(experiment, distribution)

        self.assertEqual(agents[0].profile.hearing_profile, "normal")
        self.assertEqual(
            agents[0].profile.auditory_functional_status,
            "functional_difficulty_confirmed",
        )

    def test_invalid_functional_status_is_rejected(self):
        from src.agents.agent import AgentProfile

        profile = AgentProfile(
            age_group="working_age_adult",
            hearing_profile="normal",
            geography="metropolitan",
            auditory_functional_status="hidden_hearing_loss",
        )

        with self.assertRaises(ValueError):
            profile.validate()

    def test_functional_status_is_in_agent_summary(self):
        agents = generate_population(
            self.experiment,
            self.distribution,
        )

        for agent in agents:
            self.assertIn(
                "auditory_functional_status",
                agent.summary(),
            )


if __name__ == "__main__":
    unittest.main()
