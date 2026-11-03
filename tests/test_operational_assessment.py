"""Tests for integrated operational assessment."""

import pytest
from src.service_capacity.funding import OperationalFunding


from src.service_capacity.age_suitability import AgeServiceSuitability
from src.service_capacity.costs import OperationalCost
from src.service_capacity.deployment import MobileServiceDeployment
from src.service_capacity.geographic_access import GeographicRoute
from src.service_capacity.operational_assessment import (
    assess_service_operations,
)
from src.service_capacity.workforce import WorkforceMember

def test_integrated_assessment_includes_funding_sufficiency():
    funding = OperationalFunding(
        funding_id="FUND-001",
        funding_source="Government",
        funding_program="Regional Hearing Services",
        available_amount_aud=31000,
        period_months=12,
        service_types=["audiology_assessment"],
        target_geographies=["regional"],
        evidence_status="simulation_assumption",
    )

    result = assess_service_operations(
        **make_inputs(),
        planned_trips_per_month=4,
        planned_appointments_per_month=24,
        planned_clinical_hours_per_month=24,
        funding_records=[funding],
        geography="regional",
        operating_months=12,
    )

    assert result.assessment_status == "assessed"
    assert result.cost_assessment.total_operational_cost_aud == 2508
    assert result.funding_assessment.total_available_funding_aud == 31000
    assert result.funding_assessment.estimated_operational_cost_aud == 30096
    assert result.funding_assessment.funding_balance_aud == 904
    assert result.funding_assessment.assessment_status == "sufficient"

def make_inputs(suitability_status="suitable"):
    workforce = WorkforceMember(
        clinician_id="CLINICIAN-001",
        role="audiologist",
        qualifications=["Audiology qualification"],
        service_types=["audiology_assessment"],
        supported_age_groups=["working_age_adult"],
        available_clinical_hours_per_month=24,
        appointment_duration_minutes=60,
        evidence_status="simulation_assumption",
    )

    route = GeographicRoute(
        route_id="ROUTE-001",
        service_id="SERVICE-001",
        destination_geography="regional",
        round_trip_distance_km=200,
        round_trip_travel_hours=4,
        maximum_round_trip_distance_km=300,
        available_travel_hours_per_month=16,
        evidence_status="simulation_assumption",
    )

    deployment = MobileServiceDeployment(
        deployment_id="DEPLOYMENT-001",
        service_id="SERVICE-001",
        route_id="ROUTE-001",
        service_types=["audiology_assessment"],
        target_age_groups=["working_age_adult"],
        service_delivery_hours_per_trip=6,
        evidence_status="simulation_assumption",
    )

    suitability = AgeServiceSuitability(
        age_group="working_age_adult",
        service_type="audiology_assessment",
        suitability_status=suitability_status,
        requirements=[],
        limitations=[],
        evidence_status="simulation_assumption",
    )

    values = {
        "clinician_labour_per_hour": 50.0,
        "travel_per_trip": 200.0,
        "equipment_per_appointment": 10.0,
        "consumables_per_appointment": 5.0,
        "other_per_trip": 25.0,
        "other_per_appointment": 2.0,
    }

    costs = [
        OperationalCost(
            cost_id=f"COST-{index:03d}",
            cost_component=component,
            service_type="audiology_assessment",
            amount_aud=amount,
            evidence_status="simulation_assumption",
            description=f"Illustrative {component} cost",
        )
        for index, (component, amount) in enumerate(values.items(), start=1)
    ]

    return {
        "workforce": workforce,
        "route": route,
        "deployment": deployment,
        "suitability": suitability,
        "service_type": "audiology_assessment",
        "age_group": "working_age_adult",
        "costs": costs,
    }


def test_restricted_capacity_stops_operational_assessment():
    result = assess_service_operations(
        **make_inputs(suitability_status="not_suitable"),
        planned_trips_per_month=4,
        planned_appointments_per_month=24,
        planned_clinical_hours_per_month=24,
    )

    assert result.assessment_status == "capacity_restricted"
    assert result.planned_schedule is None
    assert result.cost_assessment is None
    assert result.funding_assessment is None


def test_available_capacity_without_schedule_requests_schedule():
    result = assess_service_operations(**make_inputs())

    assert result.assessment_status == "schedule_required"
    assert result.capacity_assessment.assessment_status == "eligible"
    assert result.planned_schedule is None
    assert result.cost_assessment is None
    assert result.funding_assessment is None


def test_valid_schedule_calculates_operational_costs():
    result = assess_service_operations(
        **make_inputs(),
        planned_trips_per_month=4,
        planned_appointments_per_month=24,
        planned_clinical_hours_per_month=24,
    )

    assert result.assessment_status == "assessed"
    assert result.planned_schedule.planned_appointments_per_month == 24
    assert result.cost_assessment.total_operational_cost_aud == 2508
    assert result.cost_assessment.cost_completeness == "complete"
    assert result.funding_assessment is None


def test_partial_schedule_inputs_are_rejected():
    with pytest.raises(ValueError, match="must all be supplied"):
        assess_service_operations(
            **make_inputs(),
            planned_trips_per_month=4,
        )


def test_schedule_without_costs_is_rejected():
    inputs = make_inputs()
    inputs.pop("costs")

    with pytest.raises(ValueError, match="costs must be supplied"):
        assess_service_operations(
            **inputs,
            planned_trips_per_month=4,
            planned_appointments_per_month=24,
            planned_clinical_hours_per_month=24,
        )
