import json

import pytest

from src.country_config import (
    load_country_profile,
    validate_country_profile,
)


@pytest.fixture
def valid_country_profile():
    return {
        "country_profile_id": "TEST-001",
        "country_name": "Test Country",
        "profile_type": "country_specific",
        "evidence_status": "simulation_assumption",
        "currency": {
            "code": "TST",
            "name": "Test currency",
        },
        "healthcare_system": {
            "funding_pathways": ["public", "private", "unknown"],
        },
        "service_context": {
            "geographies": ["urban", "rural"],
        },
    }


def test_valid_country_profile_passes_validation(valid_country_profile):
    assert validate_country_profile(valid_country_profile) is True


def test_country_profile_loads_from_json(tmp_path, valid_country_profile):
    path = tmp_path / "country.json"
    path.write_text(json.dumps(valid_country_profile), encoding="utf-8")

    result = load_country_profile(path)

    assert result["country_name"] == "Test Country"
    assert result["currency"]["code"] == "TST"


def test_missing_country_profile_raises_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_country_profile(tmp_path / "missing.json")


def test_missing_required_field_is_rejected(valid_country_profile):
    del valid_country_profile["country_name"]

    with pytest.raises(ValueError, match="country_name"):
        validate_country_profile(valid_country_profile)


def test_empty_funding_pathways_are_rejected(valid_country_profile):
    valid_country_profile["healthcare_system"]["funding_pathways"] = []

    with pytest.raises(ValueError, match="Funding pathways"):
        validate_country_profile(valid_country_profile)


def test_duplicate_funding_pathways_are_rejected(valid_country_profile):
    valid_country_profile["healthcare_system"]["funding_pathways"] = [
        "public",
        "public",
    ]

    with pytest.raises(ValueError, match="Funding pathways"):
        validate_country_profile(valid_country_profile)


def test_empty_geographies_are_rejected(valid_country_profile):
    valid_country_profile["service_context"]["geographies"] = []

    with pytest.raises(ValueError, match="Geographies"):
        validate_country_profile(valid_country_profile)


def test_duplicate_geographies_are_rejected(valid_country_profile):
    valid_country_profile["service_context"]["geographies"] = [
        "urban",
        "urban",
    ]

    with pytest.raises(ValueError, match="Geographies"):
        validate_country_profile(valid_country_profile)
def test_invalid_json_raises_clear_error(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text("{ invalid json", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid country profile JSON"):
        load_country_profile(path)


def test_notes_must_be_a_list_of_non_empty_strings(valid_country_profile):
    valid_country_profile["notes"] = ["Valid note", ""]

    with pytest.raises(ValueError, match="Notes"):
        validate_country_profile(valid_country_profile)