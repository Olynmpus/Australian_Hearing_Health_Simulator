"""Generate synthetic individuals for hearing-health simulations.

Generated distributions are scenario assumptions, not population estimates.
Communication preferences are not inferred from age or hearing profile.
"""

import math
import random

from src.agents.agent import (
    Agent,
    AgentProfile,
    AgentCommunicationProfile,
)


def _validate_categories(name, categories):
    if not isinstance(categories, list) or not categories:
        raise ValueError(f"{name} must be a non-empty list.")

    if any(not isinstance(item, str) or not item.strip()
           for item in categories):
        raise ValueError(f"{name} must contain non-empty strings.")

    if len(categories) != len(set(categories)):
        raise ValueError(f"{name} contains duplicate categories.")


def _validate_weights(name, categories, weights):
    if not isinstance(weights, dict):
        raise ValueError(f"Weights for {name} must be a dictionary.")

    if set(weights) != set(categories):
        raise ValueError(
            f"Weights for {name} must match its configured categories."
        )

    values = []

    for category in categories:
        value = weights[category]

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
        ):
            raise ValueError(
                f"Invalid weight for {name}.{category}: {value}"
            )

        values.append(value)

    if sum(values) <= 0:
        raise ValueError(f"At least one {name} weight must be positive.")

    return values


def generate_population(
    experiment_config,
    distribution_config,
    vocabulary=None,
):
    """Generate agents from experiment and synthetic distribution settings.

    Returns:
        list[Agent]: Generated individual agents.

    The same configured random seed and inputs produce the same population.
    """

    if not isinstance(experiment_config, dict):
        raise ValueError("experiment_config must be a dictionary.")

    if not isinstance(distribution_config, dict):
        raise ValueError("distribution_config must be a dictionary.")

    if distribution_config.get("evidence_status") != "simulation_assumption":
        raise ValueError(
            "This generator requires an explicitly labelled "
            "simulation_assumption distribution."
        )

    population_config = experiment_config.get("population", {})
    hearing_config = experiment_config.get("hearing_profiles", {})
    auditory_function_config = experiment_config.get("auditory_function", {})
    simulation_config = experiment_config.get("simulation", {})

    population_size = population_config.get("size")

    if (
        isinstance(population_size, bool)
        or not isinstance(population_size, int)
        or population_size <= 0
    ):
        raise ValueError("Population size must be a positive integer.")

    seed = simulation_config.get("random_seed")

    if seed is not None and (
        isinstance(seed, bool) or not isinstance(seed, int)
    ):
        raise ValueError("random_seed must be an integer or None.")

    categories = {
        "age_groups": population_config.get("age_groups"),
        "hearing_profiles": hearing_config.get("categories"),
        "geography": list(population_config.get("geography", {}).keys()),
        "onset_types": hearing_config.get("onset_types"),
        "progression_types": hearing_config.get("progression_types"),
        "auditory_functional_status": (auditory_function_config.get("functional_statuses")),
    }

    weights_config = distribution_config.get("weights", {})
    validated_weights = {}

    for name, values in categories.items():
        _validate_categories(name, values)

        if name == "geography":
            # Geography weights are already specified in the experiment file.
            weights = population_config["geography"]
        else:
            weights = weights_config.get(name)

        validated_weights[name] = _validate_weights(
            name,
            values,
            weights,
        )

    rng = random.Random(seed)

    sampled_values = {
        name: rng.choices(
            categories[name],
            weights=validated_weights[name],
            k=population_size,
        )
        for name in categories
    }

    agents = []

    for index in range(population_size):
        profile = AgentProfile(
            age_group=sampled_values["age_groups"][index],
            hearing_profile=sampled_values["hearing_profiles"][index],
            auditory_functional_status=sampled_values["auditory_functional_status"][index],
            geography=sampled_values["geography"][index],
            onset_type=sampled_values["onset_types"][index],
            progression_type=sampled_values["progression_types"][index],
            communication_profile=AgentCommunicationProfile(),
        )

        agent = Agent(
            agent_id=f"PERSON-{index + 1:06d}",
            profile=profile,
        )

        agent.validate(vocabulary)
        agents.append(agent)

    return agents
