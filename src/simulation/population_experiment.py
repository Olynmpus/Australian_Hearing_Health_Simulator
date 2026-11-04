"""Initial population experiment setup."""

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from src.config_loader import load_experiment_config
from src.country_config import load_country_profile
from src.population.generator import generate_population
from src.population.integration import create_hearing_support_records
from src.hearing_support.need import HearingSupportNeed

@dataclass
class PopulationExperiment:
    """Initialised synthetic population experiment."""

    experiment_id: str
    experiment_name: str
    country_profile_id: str
    country_name: str
    population_size: int
    duration_months: int
    random_seed: int | None
    distribution_profile_id: str
    evidence_status: str
    agents: list
    support_records: list

    def summary(self):
        """Return population counts and profile distributions."""

        def distribution(values):
            values = list(values)
            counts = Counter(values)
            total = len(values)
            return {
                category: {
                    "count": count,
                    "percentage": round(count / total * 100, 1),
                }
                for category, count in sorted(counts.items())
            }

        return {
            "experiment_id": self.experiment_id,
            "experiment_name": self.experiment_name,
            "country_profile_id": self.country_profile_id,
            "country_name": self.country_name,
            "population_size": self.population_size,
            "duration_months": self.duration_months,
            "random_seed": self.random_seed,
            "distribution_profile_id": self.distribution_profile_id,
            "evidence_status": self.evidence_status,
            "agent_count": len(self.agents),
            "support_record_count": len(self.support_records),
            "population_distributions": {
                "age_group": distribution(
                    agent.profile.age_group for agent in self.agents
                ),
                "hearing_profile": distribution(
                    agent.profile.hearing_profile for agent in self.agents
                ),
                "geography": distribution(
                    agent.profile.geography for agent in self.agents
                ),
                "functional_status": distribution(
                    agent.profile.auditory_functional_status
                    for agent in self.agents
                ),
            },
        }

def initialise_hearing_support_needs(support_records):
    """Create an initial month-zero need assessment for each individual.

    Functional difficulty is preserved from the agent profile.
    Perceived need and help-seeking intention remain unknown.
    """

    for record in support_records:
        need = HearingSupportNeed(
            agent_id=record.agent_id,
            assessment_month=0,
            functional_difficulty_status=(
                record.agent.profile.auditory_functional_status
            ),
            perceived_need="unknown",
            help_seeking_intention="unknown",
            help_seeking_action="unknown",
            evidence_status="simulation_assumption",
        )

        record.add_hearing_support_need(need)

    return support_records

def run_population_experiment(
    experiment_config_path,
    distribution_config_path,
):
    """Load configurations and initialise the synthetic population."""

    experiment_config = load_experiment_config(
        experiment_config_path
    )

    experiment_path = Path(experiment_config_path).resolve()

    country_profile_path = (
        experiment_path.parent
        / experiment_config["country_profile"]
    )

    country_profile = load_country_profile(country_profile_path)

    distribution_path = Path(distribution_config_path)

    if not distribution_path.exists():
        raise FileNotFoundError(
            f"Population configuration not found: {distribution_path}"
        )

    with distribution_path.open("r", encoding="utf-8-sig") as file:
        distribution_config = json.load(file)

    if not isinstance(distribution_config, dict):
        raise ValueError(
            "Population distribution configuration must be an object."
        )

    agents = generate_population(
        experiment_config,
        distribution_config,
    )

    support_records = create_hearing_support_records(agents)
    support_records = initialise_hearing_support_needs(
    support_records
)

    return PopulationExperiment(
        experiment_id=experiment_config["experiment_id"],
        experiment_name=experiment_config.get(
            "experiment_name",
            experiment_config["experiment_id"],
        ),
        country_profile_id=country_profile["country_profile_id"],
        country_name=country_profile["country_name"],
        population_size=len(agents),
        duration_months=experiment_config["simulation"]["duration_months"],
        random_seed=experiment_config["simulation"].get("random_seed"),
        distribution_profile_id=distribution_config.get(
            "profile_id",
            "unknown",
        ),
        evidence_status=distribution_config["evidence_status"],
        agents=agents,
        support_records=support_records,
    )
