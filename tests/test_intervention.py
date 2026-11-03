import pytest

from src.interventions.intervention import Intervention


def make_intervention(**overrides):
    values = {
        "intervention_id": "INT-001",
        "name": "Mobile hearing outreach",
        "description": "Mobile assessment services.",
        "intervention_type": "service",
        "target_geographies": ["regional", "remote_very_remote"],
        "intended_service_change": "Provide an additional assessment pathway.",
        "evidence_status": "simulation_assumption",
        "assumptions": ["Service capacity is established."],
    }

    values.update(overrides)
    return Intervention(**values)


def test_valid_intervention():
    intervention = make_intervention()

    assert intervention.validate() is True


def test_intervention_serialises_correctly():
    result = make_intervention().to_dict()

    assert result["intervention_id"] == "INT-001"
    assert result["intervention_type"] == "service"
    assert result["target_geographies"] == [
        "regional",
        "remote_very_remote",
    ]


@pytest.mark.parametrize(
    "field,value",
    [
        ("intervention_id", ""),
        ("name", ""),
        ("description", ""),
        ("intended_service_change", ""),
        ("intervention_type", "unknown"),
        ("evidence_status", "unverified"),
        ("intervention_type", []),
        ("evidence_status", {}),
        ("target_geographies", []),
        ("target_geographies", ["regional", "regional"]),
        ("target_geographies", ["invalid"]),
        ("target_geographies", [["regional"]]),
        ("assumptions", "not a list"),
        ("assumptions", [""]),
    ],
)
def test_invalid_intervention_is_rejected(field, value):
    intervention = make_intervention(**{field: value})

    with pytest.raises(ValueError):
        intervention.validate()


def test_assumptions_can_be_empty():
    intervention = make_intervention(assumptions=[])

    assert intervention.validate() is True
