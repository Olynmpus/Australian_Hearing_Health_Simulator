"""Loading and validation of country reference profiles."""

import json
from pathlib import Path


def load_country_profile(config_path):
    """Load and validate a country profile."""

    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Country profile not found: {path}"
        )

    try:
        with path.open("r", encoding="utf-8-sig") as file:
            profile = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid country profile JSON: {path}"
        ) from error
    
    validate_country_profile(profile)

    return profile


def validate_country_profile(profile):
    """Validate the basic structure of a country profile."""

    if not isinstance(profile, dict):
        raise ValueError("Country profile must be a JSON object.")

    required_fields = [
        "country_profile_id",
        "country_name",
        "profile_type",
        "evidence_status",
        "currency",
        "healthcare_system",
        "service_context",
    ]

    for field in required_fields:
        if field not in profile:
            raise ValueError(
                f"Missing country profile field: {field}"
            )

    for field in [
        "country_profile_id",
        "country_name",
        "profile_type",
        "evidence_status",
    ]:
        if not isinstance(profile[field], str) or not profile[field].strip():
            raise ValueError(
                f"Country profile field must be a non-empty string: {field}"
            )

    currency = profile["currency"]

    if not isinstance(currency, dict):
        raise ValueError("Currency configuration must be an object.")

    for field in ["code", "name"]:
        if not isinstance(currency.get(field), str) or not currency[field].strip():
            raise ValueError(
                f"Currency field must be a non-empty string: {field}"
            )

    healthcare = profile["healthcare_system"]

    if not isinstance(healthcare, dict):
        raise ValueError("Healthcare system must be an object.")

    pathways = healthcare.get("funding_pathways")

    if (
        not isinstance(pathways, list)
        or not pathways
        or any(not isinstance(item, str) or not item.strip() for item in pathways)
        or len(pathways) != len(set(pathways))
    ):
        raise ValueError(
            "Funding pathways must be a non-empty list of unique strings."
        )

    service_context = profile["service_context"]

    if not isinstance(service_context, dict):
        raise ValueError("Service context must be an object.")

    geographies = service_context.get("geographies")

    if (
        not isinstance(geographies, list)
        or not geographies
        or any(not isinstance(item, str) or not item.strip() for item in geographies)
        or len(geographies) != len(set(geographies))
    ):
        raise ValueError(
            "Geographies must be a non-empty list of unique strings."
        )

    notes = profile.get("notes", [])

    if (
        not isinstance(notes, list)
        or any(
            not isinstance(note, str) or not note.strip()
            for note in notes
        )
    ):
        raise ValueError(
            "Notes must be a list of non-empty strings."
        )
    
    return True
