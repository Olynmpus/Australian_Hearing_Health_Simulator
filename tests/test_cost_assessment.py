from dataclasses import replace

import pytest

from src.service_capacity.assessment import assess_mobile_service_capacity
from src.service_capacity.age_suitability import AgeServiceSuitability
from src.service_capacity.costs import OperationalCost
from src.service_capacity.cost_assessment import assess_operational_costs
from src.service_capacity.deployment import MobileServiceDeployment
from src.service_capacity.geographic_access import GeographicRoute
from src.service_capacity.planned_schedule import (
    create_planned_service_schedule,
)
from src.service_capacity.workforce import WorkforceMember


def make_costs():
    values = {
        "clinician_labour_per_hour": 50.0,
        "travel_per_trip": 200.0,
        "equipment_per_appointment": 10.0,
        "consumables_per_appointment": 5.0,
        "other_per_trip": 25.0,
        "other_per_appointment": 2.0,
    }

    return [
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


def make_schedule(trips=4, appointments=24, hours=24):
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
        suitability_status="suitable",
        requirements=[],
        limitations=[],
        evidence_status="simulation_assumption",
    )

    assessment = assess_mobile_service_capacity(
        workforce,
        route,
        deployment,
        suitability,
        "audiology_assessment",
        "working_age_adult",
    )

    return create_planned_service_schedule(
        capacity_assessment=assessment,
        workforce=workforce,
        deployment=deployment,
        planned_trips_per_month=trips,
        planned_appointments_per_month=appointments,
        planned_clinical_hours_per_month=hours,
    )


def assess(costs=None, schedule=None):
    return assess_operational_costs(
        costs=make_costs() if costs is None else costs,
        service_type="audiology_assessment",
        planned_schedule=make_schedule() if schedule is None else schedule,
    )


def test_calculates_total_operational_cost():
    result = assess()

    assert result.planned_trips_per_month == 4
    assert result.planned_appointments_per_month == 24
    assert result.planned_clinical_hours_per_month == 24
    assert result.component_costs_aud["clinician_labour_per_hour"] == 1200
    assert result.component_costs_aud["travel_per_trip"] == 800
    assert result.component_costs_aud["equipment_per_appointment"] == 240
    assert result.component_costs_aud["consumables_per_appointment"] == 120
    assert result.component_costs_aud["other_per_trip"] == 100
    assert result.component_costs_aud["other_per_appointment"] == 48
    assert result.total_operational_cost_aud == 2508
    assert result.cost_completeness == "complete"


def test_underutilised_schedule_calculates_costs_from_planned_activity():
    result = assess(schedule=make_schedule(
        trips=1,
        appointments=4,
        hours=4,
    ))

    assert result.planned_trips_per_month == 1
    assert result.planned_appointments_per_month == 4
    assert result.planned_clinical_hours_per_month == 4
    assert result.total_operational_cost_aud == 493


def test_zero_activity_produces_zero_cost():
    result = assess(schedule=make_schedule(
        trips=0,
        appointments=0,
        hours=0,
    ))

    assert result.planned_appointments_per_month == 0
    assert result.total_operational_cost_aud == 0


def test_unknown_cost_prevents_complete_total():
    costs = make_costs()
    costs[0].amount_aud = None
    costs[0].evidence_status = "unknown"

    result = assess(costs=costs)

    assert result.total_operational_cost_aud is None
    assert result.cost_completeness == "incomplete"
    assert "clinician_labour_per_hour" in result.unknown_cost_components


def test_zero_cost_is_included_in_complete_total():
    costs = make_costs()
    costs[1].amount_aud = 0

    result = assess(costs=costs)

    assert result.total_operational_cost_aud == 1708
    assert result.cost_completeness == "complete"


def test_missing_component_is_rejected():
    costs = make_costs()[:-1]

    with pytest.raises(ValueError, match="Missing explicit cost components"):
        assess(costs=costs)


def test_duplicate_component_is_rejected():
    costs = make_costs()
    costs.append(costs[0])

    with pytest.raises(ValueError, match="Duplicate cost component"):
        assess(costs=costs)


def test_mismatched_service_type_is_rejected():
    costs = make_costs()
    costs[0].service_type = "rehabilitation"

    with pytest.raises(ValueError, match="must match"):
        assess(costs=costs)


@pytest.mark.parametrize(
    "field,value",
    [
        ("planned_trips_per_month", -1),
        ("planned_trips_per_month", 1.5),
        ("planned_trips_per_month", True),
        ("planned_appointments_per_month", -1),
        ("planned_appointments_per_month", 1.5),
        ("planned_appointments_per_month", True),
        ("planned_clinical_hours_per_month", -1),
        ("planned_clinical_hours_per_month", float("nan")),
        ("planned_clinical_hours_per_month", float("inf")),
        ("planned_clinical_hours_per_month", True),
    ],
)
def test_invalid_schedule_activity_is_rejected(field, value):
    schedule = replace(make_schedule(), **{field: value})

    with pytest.raises(ValueError):
        assess(schedule=schedule)


def test_rejects_invalid_schedule_status():
    schedule = replace(make_schedule(), schedule_status="invalid")

    with pytest.raises(ValueError, match="valid status"):
        assess(schedule=schedule)


def test_rejects_mismatched_schedule_service_type():
    schedule = replace(
        make_schedule(),
        service_type="rehabilitation",
    )

    with pytest.raises(ValueError, match="match the selected service"):
        assess(schedule=schedule)


def test_rejects_invalid_cost_object():
    with pytest.raises(TypeError, match="OperationalCost"):
        assess(costs=["not a cost"])


def test_rejects_invalid_schedule_object():
    with pytest.raises(TypeError, match="PlannedServiceSchedule"):
        assess(schedule="not a schedule")


def test_serialises_assessment():
    result = assess()
    data = result.to_dict()

    assert data["total_operational_cost_aud"] == 2508
    assert data["cost_completeness"] == "complete"
    assert data["planned_appointments_per_month"] == 24
    assert len(data["evidence_statuses"]) == 6
