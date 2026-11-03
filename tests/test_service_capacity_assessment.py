"""Tests for integrated mobile service capacity assessment."""

from dataclasses import replace

import pytest

from src.service_capacity.age_suitability import AgeServiceSuitability
from src.service_capacity.assessment import assess_mobile_service_capacity
from src.service_capacity.deployment import MobileServiceDeployment
from src.service_capacity.geographic_access import GeographicRoute
from src.service_capacity.workforce import WorkforceMember


def make_workforce(
    clinical_hours=20,
    service_types=None,
    supported_age_groups=None,
):
    return WorkforceMember(
        clinician_id="CLINICIAN-001",
        role="audiologist",
        qualifications=["Audiology qualification"],
        service_types=service_types or ["audiology_assessment"],
        supported_age_groups=(
            supported_age_groups or ["working_age_adult"]
        ),
        available_clinical_hours_per_month=clinical_hours,
        appointment_duration_minutes=60,
        evidence_status="simulation_assumption",
    )


def make_route(route_id="ROUTE-001", service_id="SERVICE-001"):
    return GeographicRoute(
        route_id=route_id,
        service_id=service_id,
        destination_geography="regional",
        round_trip_distance_km=200,
        round_trip_travel_hours=4,
        maximum_round_trip_distance_km=300,
        available_travel_hours_per_month=8,
        evidence_status="simulation_assumption",
    )


def make_deployment(
    route_id="ROUTE-001",
    service_id="SERVICE-001",
    service_types=None,
    target_age_groups=None,
):
    return MobileServiceDeployment(
        deployment_id="DEPLOYMENT-001",
        service_id=service_id,
        route_id=route_id,
        service_types=service_types or ["audiology_assessment"],
        target_age_groups=(
            target_age_groups or ["working_age_adult"]
        ),
        service_delivery_hours_per_trip=6,
        evidence_status="simulation_assumption",
    )


def make_suitability(status="suitable"):
    return AgeServiceSuitability(
        age_group="working_age_adult",
        service_type="audiology_assessment",
        suitability_status=status,
        requirements=[],
        limitations=[],
        evidence_status="simulation_assumption",
    )


def assess(
    workforce=None,
    route=None,
    deployment=None,
    suitability=None,
):
    return assess_mobile_service_capacity(
        workforce=workforce or make_workforce(),
        route=route or make_route(),
        deployment=deployment or make_deployment(),
        suitability=suitability or make_suitability(),
        service_type="audiology_assessment",
        age_group="working_age_adult",
    )


def test_calculates_deliverable_capacity_limited_by_travel():
    result = assess()

    assert result.workforce_service_capacity_per_month == 20
    assert result.trips_per_month == 2
    assert result.appointments_per_trip == 6
    assert result.travel_supported_appointments_per_month == 12
    assert result.deliverable_capacity_per_month == 12
    assert result.assessment_status == "eligible"
    assert result.limiting_constraints == ["travel"]


def test_calculates_deliverable_capacity_limited_by_workforce():
    result = assess(workforce=make_workforce(clinical_hours=5))

    assert result.workforce_service_capacity_per_month == 5
    assert result.travel_supported_appointments_per_month == 12
    assert result.deliverable_capacity_per_month == 5
    assert result.limiting_constraints == ["workforce"]


def test_equal_workforce_and_travel_capacity_reports_both_constraints():
    workforce = make_workforce(clinical_hours=12)

    result = assess(workforce=workforce)

    assert result.deliverable_capacity_per_month == 12
    assert result.limiting_constraints == ["workforce", "travel"]


def test_unsupported_workforce_age_scope_blocks_deliverable_capacity():
    workforce = make_workforce(
        supported_age_groups=["adolescent"]
    )

    result = assess(workforce=workforce)

    assert result.workforce_service_capacity_per_month == 20
    assert result.workforce_age_scope_supported is False
    assert result.travel_supported_appointments_per_month == 12
    assert result.deliverable_capacity_per_month == 0
    assert result.assessment_status == "restricted"
    assert "scope" in result.limiting_constraints


def test_unsupported_deployment_age_scope_blocks_deliverable_capacity():
    deployment = make_deployment(
        target_age_groups=["adolescent"]
    )

    result = assess(deployment=deployment)

    assert result.deployment_age_group_supported is False
    assert result.travel_supported_appointments_per_month == 12
    assert result.deliverable_capacity_per_month == 0
    assert "scope" in result.limiting_constraints


def test_unsupported_deployment_service_preserves_theoretical_capacity():
    deployment = make_deployment(
        service_types=["hearing_aid_fitting"]
    )

    result = assess(deployment=deployment)

    assert result.deployment_service_supported is False
    assert result.workforce_service_capacity_per_month == 20
    assert result.travel_supported_appointments_per_month == 12
    assert result.deliverable_capacity_per_month == 0
    assert "scope" in result.limiting_constraints


@pytest.mark.parametrize(
    "status",
    ["not_suitable", "assessment_required", "unknown"],
)
def test_non_suitable_or_unconfirmed_suitability_blocks_capacity(status):
    result = assess(suitability=make_suitability(status))

    assert result.suitability_status == status
    assert result.scope_eligible_workforce_capacity_per_month == 20
    assert result.travel_supported_appointments_per_month == 12
    assert result.deliverable_capacity_per_month == 0
    assert result.assessment_status == "restricted"
    assert "suitability" in result.limiting_constraints


def test_route_id_must_match_deployment():
    deployment = make_deployment(route_id="ROUTE-OTHER")

    with pytest.raises(ValueError, match="same route_id"):
        assess(deployment=deployment)


def test_service_id_must_match_between_route_and_deployment():
    deployment = make_deployment(service_id="SERVICE-OTHER")

    with pytest.raises(ValueError, match="same service_id"):
        assess(deployment=deployment)


def test_suitability_service_type_must_match_selection():
    suitability = replace(
        make_suitability(),
        service_type="hearing_aid_fitting",
    )

    with pytest.raises(ValueError, match="selected service type"):
        assess(suitability=suitability)


def test_suitability_age_group_must_match_selection():
    suitability = replace(
        make_suitability(),
        age_group="adolescent",
    )

    with pytest.raises(ValueError, match="selected age group"):
        assess(suitability=suitability)


def test_zero_travel_capacity_is_reported():
    route = replace(
        make_route(),
        available_travel_hours_per_month=0,
    )

    result = assess(route=route)

    assert result.travel_supported_appointments_per_month == 0
    assert result.deliverable_capacity_per_month == 0
    assert result.assessment_status == "zero_capacity"
    assert result.limiting_constraints == ["travel"]


def test_result_can_be_serialised():
    result = assess()
    data = result.to_dict()

    assert data["deliverable_capacity_per_month"] == 12
    assert data["funding_status"] == "not_calculated"
    assert isinstance(data["reasons"], list)


def test_invalid_input_type_is_rejected():
    with pytest.raises(TypeError, match="workforce must be"):
        assess(workforce="not a workforce member")
