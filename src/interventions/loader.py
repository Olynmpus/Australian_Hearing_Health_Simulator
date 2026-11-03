"""Load and validate hearing-health intervention definitions."""

import json
from pathlib import Path

from src.interventions.intervention import Intervention


def load_intervention(intervention_path):
    """Load an intervention definition from a JSON file."""

    path = Path(intervention_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Intervention file not found: {path}"
        )

    with path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            "Intervention configuration must be a JSON object."
        )

    try:
        intervention = Intervention(**data)
    except TypeError as exc:
        raise ValueError(
            f"Invalid intervention configuration fields: {exc}"
        ) from exc

    intervention.validate()

    return intervention
