import pytest

from src.service_capacity.assessment import assess_mobile_service_capacity
from src.service_capacity.age_suitability import AgeServiceSuitability
from src.service_capacity.deployment import MobileServiceDeployment
from src.service_capacity.geographic_access import GeographicRoute
from src.service_capacity.planned_schedule import (
    create_planned_service_schedule,
)
from src.service_capacity.workforce import WorkforceMember


def make_inputs(
    clinical_hours=20,
    travel_hours=8,
    suitability_status="suitable",
):
    workforce = WorkforceMember(
        clinician_id="CLINICIAN-001",
        role="audiologist",
        qualifications=["Audiology qualification"],
        service_types=["audiology_assessment"],
        supported_age_groups=["working_age_adult"],
        available_clinical_hours_per_month=clinical_hours,
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
        available_travel_hours_per_month=travel_hours,
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

    assessment = assess_mobile_service_capacity(
        workforce,
        route,
        deployment,
        suitability,
        "audiology_assessment",
        "working_age_adult",
    )

    return workforce, deployment, assessment


def create_schedule(
    workforce,
    deployment,
    assessment,
    trips=1,
    appointments=4,
    hours=4,
):
    return create_planned_service_schedule(
        capacity_assessment=assessment,
        workforce=workforce,
        deployment=deployment,
        planned_trips_per_month=trips,
        planned_appointments_per_month=appointments,
        planned_clinical_hours_per_month=hours,
    )


def test_accepts_underutilised_service_schedule():
    workforce, deployment, assessment = make_inputs()

    result = create_schedule(workforce, deployment, assessment)

    assert result.planned_trips_per_month == 1
    assert result.planned_appointments_per_month == 4
    assert result.planned_clinical_hours_per_month == 4
    assert result.maximum_deliverable_appointments_per_month == 12
    assert result.schedule_status == "valid"


def test_accepts_schedule_using_full_assessed_capacity():
    workforce, deployment, assessment = make_inputs()

    result = create_schedule(
        workforce,
        deployment,
        assessment,
        trips=2,
        appointments=12,
        hours=12,
    )

    assert result.planned_appointments_per_month == 12


def test_rejects_planned_trips_above_capacity():
    workforce, deployment, assessment = make_inputs()

    with pytest.raises(ValueError, match="trips exceed"):
        create_schedule(
            workforce, deployment, assessment,
            trips=3, appointments=12, hours=12,
        )


def test_rejects_appointments_above_planned_trip_capacity():
    workforce, deployment, assessment = make_inputs()

    with pytest.raises(ValueError, match="capacity of planned trips"):
        create_schedule(
            workforce, deployment, assessment,
            trips=1, appointments=7, hours=7,
        )

def test_rejects_appointments_above_deliverable_capacity():
    workforce, deployment, assessment = make_inputs(
        clinical_hours=5,
    )

    with pytest.raises(ValueError, match="deliverable capacity"):
        create_schedule(
            workforce, deployment, assessment,
            trips=2, appointments=6, hours=6,
        )

def test_rejects_insufficient_clinical_hours():
    workforce, deployment, assessment = make_inputs()

    with pytest.raises(ValueError, match="insufficient"):
        create_schedule(
            workforce, deployment, assessment,
            trips=1, appointments=4, hours=3,
        )


def test_rejects_clinical_hours_above_workforce_availability():
    workforce, deployment, assessment = make_inputs(
        clinical_hours=5,
    )

    with pytest.raises(ValueError, match="workforce availability"):
        create_schedule(
            workforce, deployment, assessment,
            trips=1, appointments=4, hours=6,
        )


def test_rejects_clinical_hours_above_deployment_hours():
    workforce, deployment, assessment = make_inputs()

    with pytest.raises(ValueError, match="deployment delivery hours"):
        create_schedule(
            workforce, deployment, assessment,
            trips=1, appointments=4, hours=7,
        )


def test_rejects_schedule_when_capacity_is_restricted():
    workforce, deployment, assessment = make_inputs(
        suitability_status="assessment_required",
    )

    with pytest.raises(ValueError, match="eligible"):
        create_schedule(workforce, deployment, assessment)


def test_accepts_zero_delivery_when_no_capacity_is_planned():
    workforce, deployment, assessment = make_inputs()

    result = create_schedule(
        workforce, deployment, assessment,
        trips=0, appointments=0, hours=0,
    )

    assert result.planned_trips_per_month == 0
    assert result.planned_appointments_per_month == 0
    assert result.planned_clinical_hours_per_month == 0


@pytest.mark.parametrize(
    "trips,appointments,hours",
    [
        (-1, 0, 0),
        (1, -1, 0),
        (1, 1, -1),
        (1.5, 1, 1),
        (1, 1.5, 1),
        (1, 1, float("nan")),
        (1, 1, float("inf")),
        (True, 1, 1),
    ],
)
def test_rejects_invalid_schedule_values(
    trips, appointments, hours
):
    workforce, deployment, assessment = make_inputs()

    with pytest.raises(ValueError):
        create_schedule(
            workforce, deployment, assessment,
            trips=trips,
            appointments=appointments,
            hours=hours,
        )


def test_schedule_can_be_serialised():
    workforce, deployment, assessment = make_inputs()

    result = create_schedule(workforce, deployment, assessment)
    data = result.to_dict()

    assert data["service_id"] == "SERVICE-001"
    assert data["service_type"] == "audiology_assessment"
    assert data["schedule_status"] == "valid"
