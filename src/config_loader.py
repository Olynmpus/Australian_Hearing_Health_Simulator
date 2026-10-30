import json
from pathlib import Path


def load_experiment_config(config_path):
    """
    Load an experiment configuration from a JSON file.
    """

    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8-sig") as file:
        config = json.load(file)

    validate_config(config)

    return config


def validate_config(config):
    """
    Check the basic validity of the experiment configuration.
    """

    required_sections = [
        "experiment_id",
        "population",
        "awareness",
        "access",
        "simulation"
    ]

    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing configuration section: {section}")

    population_size = config["population"]["size"]

    if population_size <= 0:
        raise ValueError("Population size must be greater than zero.")

    geography = config["population"]["geography"]

    if sum(geography.values()) != 100:
        raise ValueError("Geographic percentages must add up to 100.")

    awareness = config["awareness"]["initial_awareness_rate"]

    if not 0 <= awareness <= 1:
        raise ValueError("Awareness rate must be between 0 and 1.")

    duration = config["simulation"]["duration_months"]

    if duration <= 0:
        raise ValueError("Simulation duration must be greater than zero.")

    return True


if __name__ == "__main__":

    config_file = Path(__file__).parent.parent / "config" / "HH-EXP-001.json"

    experiment = load_experiment_config(config_file)

    print("Experiment configuration loaded successfully.")
    print("---------------------------------------------")
    print("Experiment:", experiment["experiment_id"])
    print("Population:", experiment["population"]["size"])
    print("Awareness:", experiment["awareness"]["initial_awareness_rate"])
    print("Duration:", experiment["simulation"]["duration_months"], "months")
    print("Repetitions:", experiment["simulation"]["number_of_repetitions"])
