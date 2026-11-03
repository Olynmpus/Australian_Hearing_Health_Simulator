import pytest

from src.service_capacity.costs import (
    COST_COMPONENT_TYPES,
    OperationalCost,
)


def make_cost(**overrides):
    values = {
        "cost_id": "COST-001",
        "cost_component": "clinician_labour_per_hour",
        "service_type": "audiology_assessment",
        "amount_aud": 100.0,
        "evidence_status": "simulation_assumption",
        "description": "Illustrative clinician labour cost per hour",
    }

    values.update(overrides)
    return OperationalCost(**values)


def test_valid_operational_cost():
    assert make_cost().validate() is True


def test_all_cost_components_are_supported():
    for component in COST_COMPONENT_TYPES:
        assert make_cost(cost_component=component).validate() is True


def test_zero_cost_is_valid():
    assert make_cost(amount_aud=0).validate() is True


def test_serialises_operational_cost():
    result = make_cost().to_dict()

    assert result["cost_id"] == "COST-001"
    assert result["cost_component"] == "clinician_labour_per_hour"
    assert result["service_type"] == "audiology_assessment"
    assert result["amount_aud"] == 100.0
    assert result["evidence_status"] == "simulation_assumption"


@pytest.mark.parametrize(
    "field,value",
    [
        ("cost_id", ""),
        ("description", ""),
        ("cost_component", "unknown_cost"),
        ("service_type", "invalid_service"),
        ("amount_aud", -1),
        ("amount_aud", float("nan")),
        ("amount_aud", float("inf")),
        ("amount_aud", True),
        ("evidence_status", "unverified"),
    ],
)
def test_invalid_operational_cost_is_rejected(field, value):
    cost = make_cost(**{field: value})

    with pytest.raises(ValueError):
        cost.validate()


@pytest.mark.parametrize(
    "field,value",
    [
        ("cost_id", None),
        ("description", None),
        ("cost_component", None),
        ("service_type", None),
        ("evidence_status", None),
    ],
)
def test_missing_operational_cost_values_are_rejected(field, value):
    cost = make_cost(**{field: value})

    with pytest.raises(ValueError):
        cost.validate()
