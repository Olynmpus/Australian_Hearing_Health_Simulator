import pytest

from src.service_capacity.funding import OperationalFunding


def make_funding(**overrides):
    values = {
        "funding_id": "FUND-001",
        "funding_source": "Government funding",
        "funding_program": "Mobile hearing outreach",
        "available_amount_aud": 250000,
        "period_months": 12,
        "service_types": ["audiology_assessment"],
        "target_geographies": ["regional", "remote_very_remote"],
        "evidence_status": "simulation_assumption",
    }

    values.update(overrides)
    return OperationalFunding(**values)


def test_valid_operational_funding():
    assert make_funding().validate() is True


def test_zero_funding_is_valid():
    assert make_funding(available_amount_aud=0).validate() is True


def test_serialises_operational_funding():
    result = make_funding().to_dict()

    assert result["funding_id"] == "FUND-001"
    assert result["available_amount_aud"] == 250000
    assert result["period_months"] == 12
    assert result["target_geographies"] == [
        "regional",
        "remote_very_remote",
    ]


@pytest.mark.parametrize(
    "field,value",
    [
        ("funding_id", ""),
        ("funding_source", ""),
        ("funding_program", ""),
        ("available_amount_aud", -1),
        ("available_amount_aud", float("nan")),
        ("available_amount_aud", float("inf")),
        ("available_amount_aud", True),
        ("period_months", 0),
        ("period_months", -12),
        ("period_months", 1.5),
        ("period_months", True),
        ("service_types", []),
        ("service_types", ["invalid_service"]),
        ("service_types", ["audiology_assessment"] * 2),
        ("target_geographies", []),
        ("target_geographies", ["unknown_area"]),
        ("target_geographies", ["regional", "regional"]),
        ("evidence_status", "unverified"),
    ],
)
def test_invalid_operational_funding_is_rejected(field, value):
    funding = make_funding(**{field: value})

    with pytest.raises(ValueError):
        funding.validate()


@pytest.mark.parametrize(
    "field,value",
    [
        ("service_types", "audiology_assessment"),
        ("service_types", ["audiology_assessment", []]),
        ("target_geographies", "regional"),
        ("target_geographies", ["regional", []]),
    ],
)
def test_invalid_list_contents_are_rejected(field, value):
    funding = make_funding(**{field: value})

    with pytest.raises(ValueError):
        funding.validate()
