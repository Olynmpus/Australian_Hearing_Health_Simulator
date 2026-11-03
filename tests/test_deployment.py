import pytest

from src.service_capacity.deployment import MobileServiceDeployment


def make_deployment(**overrides):
    values = {
        "deployment_id": "DEPLOY-001",
        "service_id": "MOBILE-001",
        "route_id": "ROUTE-001",
        "service_types": ["audiology_assessment"],
        "target_age_groups": ["older_adult"],
        "service_delivery_hours_per_trip": 6,
        "evidence_status": "simulation_assumption",
    }

    values.update(overrides)
    return MobileServiceDeployment(**values)


def test_valid_deployment():
    assert make_deployment().validate() is True


def test_calculates_appointments_per_trip():
    deployment = make_deployment()

    assert deployment.calculate_appointments_per_trip(60) == 6


def test_capacity_uses_whole_appointments():
    deployment = make_deployment(
        service_delivery_hours_per_trip=5,
    )

    assert deployment.calculate_appointments_per_trip(45) == 6


def test_short_delivery_period_produces_zero_appointments():
    deployment = make_deployment(
        service_delivery_hours_per_trip=0.25,
    )

    assert deployment.calculate_appointments_per_trip(60) == 0


def test_invalid_appointment_duration_is_rejected():
    deployment = make_deployment()

    for duration in (0, -30, 30.5, True):
        with pytest.raises(ValueError):
            deployment.calculate_appointments_per_trip(duration)


def test_serialises_deployment():
    result = make_deployment().to_dict()

    assert result["deployment_id"] == "DEPLOY-001"
    assert result["service_id"] == "MOBILE-001"
    assert result["route_id"] == "ROUTE-001"
    assert result["service_delivery_hours_per_trip"] == 6


@pytest.mark.parametrize(
    "field,value",
    [
        ("deployment_id", ""),
        ("service_id", ""),
        ("route_id", ""),
        ("service_types", []),
        ("service_types", ["invalid_service"]),
        ("service_types", ["audiology_assessment"] * 2),
        ("target_age_groups", []),
        ("target_age_groups", ["invalid_age_group"]),
        ("target_age_groups", ["older_adult"] * 2),
        ("service_delivery_hours_per_trip", 0),
        ("service_delivery_hours_per_trip", -1),
        ("service_delivery_hours_per_trip", float("nan")),
        ("service_delivery_hours_per_trip", float("inf")),
        ("service_delivery_hours_per_trip", True),
        ("evidence_status", "unverified"),
    ],
)
def test_invalid_deployment_is_rejected(field, value):
    deployment = make_deployment(**{field: value})

    with pytest.raises(ValueError):
        deployment.validate()


def test_service_types_and_age_groups_are_explicit():
    deployment = make_deployment(
        service_types=["communication_support"],
        target_age_groups=["infant"],
    )

    assert deployment.validate() is True
    assert deployment.service_types == ["communication_support"]
    assert deployment.target_age_groups == ["infant"]
