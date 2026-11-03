"""Integrated assessment of hearing service operational feasibility."""

from dataclasses import asdict, dataclass

from .assessment import (
    ServiceCapacityAssessment,
    assess_mobile_service_capacity,
)
from .age_suitability import AgeServiceSuitability
from .costs import OperationalCost
from .cost_assessment import (
    OperationalCostAssessment,
    assess_operational_costs,
)
from .deployment import MobileServiceDeployment
from .funding import OperationalFunding
from .funding_assessment import (
    FundingAssessment,
    assess_operational_funding,
)
from .geographic_access import GeographicRoute
from .planned_schedule import (
    PlannedServiceSchedule,
    create_planned_service_schedule,
)
from .workforce import WorkforceMember


@dataclass
class IntegratedOperationalAssessment:
    """Combined result of a hearing service operational assessment."""

    capacity_assessment: ServiceCapacityAssessment
    planned_schedule: PlannedServiceSchedule | None
    cost_assessment: OperationalCostAssessment | None
    funding_assessment: FundingAssessment | None

    assessment_status: str
    reasons: list[str]

    def to_dict(self):
        """Return the integrated assessment as a dictionary."""
        return asdict(self)


def assess_service_operations(
    workforce: WorkforceMember,
    route: GeographicRoute,
    deployment: MobileServiceDeployment,
    suitability: AgeServiceSuitability,
    service_type: str,
    age_group: str,
    costs: list[OperationalCost] | None = None,
    planned_trips_per_month: int | None = None,
    planned_appointments_per_month: int | None = None,
    planned_clinical_hours_per_month: float | None = None,
    funding_records: list[OperationalFunding] | None = None,
    geography: str | None = None,
    operating_months: int | None = None,
) -> IntegratedOperationalAssessment:
    """Coordinate capacity, planned delivery, costs and optional funding."""

    capacity = assess_mobile_service_capacity(
        workforce=workforce,
        route=route,
        deployment=deployment,
        suitability=suitability,
        service_type=service_type,
        age_group=age_group,
    )

    if capacity.assessment_status != "eligible":
        return IntegratedOperationalAssessment(
            capacity_assessment=capacity,
            planned_schedule=None,
            cost_assessment=None,
            funding_assessment=None,
            assessment_status="capacity_restricted",
            reasons=[
                "Capacity restrictions prevent the planned service "
                "assessment from proceeding."
            ],
        )

    planned_values = (
        planned_trips_per_month,
        planned_appointments_per_month,
        planned_clinical_hours_per_month,
    )

    if all(value is None for value in planned_values):
        return IntegratedOperationalAssessment(
            capacity_assessment=capacity,
            planned_schedule=None,
            cost_assessment=None,
            funding_assessment=None,
            assessment_status="schedule_required",
            reasons=[
                "Capacity is available, but an explicit delivery "
                "schedule has not been provided."
            ],
        )

    if any(value is None for value in planned_values):
        raise ValueError(
            "Planned trips, appointments and clinical hours "
            "must all be supplied together."
        )

    if costs is None:
        raise ValueError(
            "Operational costs must be supplied when a planned "
            "schedule is provided."
        )

    schedule = create_planned_service_schedule(
        capacity_assessment=capacity,
        workforce=workforce,
        deployment=deployment,
        planned_trips_per_month=planned_trips_per_month,
        planned_appointments_per_month=planned_appointments_per_month,
        planned_clinical_hours_per_month=planned_clinical_hours_per_month,
    )

    cost_assessment = assess_operational_costs(
        costs=costs,
        service_type=service_type,
        planned_schedule=schedule,
    )

    funding_assessment = None

    if funding_records is not None:
        if geography is None or operating_months is None:
            raise ValueError(
                "Geography and operating months are required "
                "when funding records are supplied."
            )

        funding_assessment = assess_operational_funding(
            funding_records=funding_records,
            cost_assessment=cost_assessment,
            service_type=service_type,
            geography=geography,
            operating_months=operating_months,
        )

    reasons = [
        "Capacity, planned delivery and operational costs "
        "have been assessed."
    ]

    if funding_assessment is not None:
        reasons.append(
            "Operational funding has also been assessed."
        )

    return IntegratedOperationalAssessment(
        capacity_assessment=capacity,
        planned_schedule=schedule,
        cost_assessment=cost_assessment,
        funding_assessment=funding_assessment,
        assessment_status="assessed",
        reasons=reasons,
    )
