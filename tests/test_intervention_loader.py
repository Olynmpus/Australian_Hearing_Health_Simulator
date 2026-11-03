import json

import pytest

from src.interventions.loader import load_intervention


CONFIG_PATH = (
    "config/interventions/mobile_hearing_outreach.json"
)


def test_load_mobile_outreach_intervention():
    intervention = load_intervention(CONFIG_PATH)

    assert intervention.intervention_id == "HH-INT-001"
    assert intervention.intervention_type == "service"
    assert intervention.evidence_status == "simulation_assumption"


def test_loader_rejects_missing_file():
    with pytest.raises(FileNotFoundError):
        load_intervention("config/interventions/missing.json")


def test_loader_rejects_invalid_json_structure(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError):
        load_intervention(path)


def test_loader_rejects_invalid_intervention(tmp_path):
    path = tmp_path / "invalid_intervention.json"

    data = {
        "intervention_id": "HH-INT-002",
        "name": "Invalid intervention",
        "description": "Test",
        "intervention_type": "unknown",
        "target_geographies": ["regional"],
        "intended_service_change": "Test change",
        "evidence_status": "simulation_assumption",
    }

    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError):
        load_intervention(path)


def test_loader_rejects_unexpected_fields(tmp_path):
    path = tmp_path / "extra_field.json"

    data = {
        "intervention_id": "HH-INT-003",
        "name": "Test intervention",
        "description": "Test",
        "intervention_type": "service",
        "target_geographies": ["regional"],
        "intended_service_change": "Test change",
        "evidence_status": "simulation_assumption",
        "unexpected_field": True,
    }

    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError):
        load_intervention(path)
