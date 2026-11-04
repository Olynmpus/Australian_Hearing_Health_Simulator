"""Initial population experiment setup."""

import json
from dataclasses import dataclass
from pathlib import Path

from src.config_loader import load_experiment_config
from src.population.generator import generate_population
from src.population.integration import create_hearing_support_records


@dataclass
class PopulationExperiment:
    """Initialised synthetic population experiment."""

    experiment_id: str
    experiment_name: str
    population_size: int
    duration_months: int
    random_seed: int | None
    distribution_profile_id: str
    evidence_status: str
    agents: list
    support_records: list

    def summary(self):
        """Return a concise experiment summary."""

        return {
            "experiment_id": self.experiment_id,
            "experiment_name": self.experiment_name,
            "population_size": self.population_size,
            "duration_months": self.duration_months,
            "random_seed": self.random_seed,
            "distribution_profile_id": self.distribution_profile_id,
            "evidence_status": self.evidence_status,
            "agent_count": len(self.agents),
            "support_record_count": len(self.support_records),
        }


def run_population_experiment(
    experiment_config_path,
    distribution_config_path,
):
    """Load configurations and initialise the synthetic population."""

    experiment_config = load_experiment_config(
        experiment_config_path
    )

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

    return PopulationExperiment(
        experiment_id=experiment_config["experiment_id"],
        experiment_name=experiment_config.get(
            "experiment_name",
            experiment_config["experiment_id"],
        ),
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
