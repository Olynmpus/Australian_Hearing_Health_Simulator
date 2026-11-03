"""Calculation of operational costs for planned hearing service delivery."""

from dataclasses import asdict, dataclass

from .costs import COST_COMPONENT_TYPES, OperationalCost
from .planned_schedule import PlannedServiceSchedule
from src.hearing_support.service_access import SERVICE_TYPES


@dataclass
class OperationalCostAssessment:
    """Calculated operational costs for a declared delivery schedule."""

    service_type: str
    planned_trips_per_month: int
    planned_appointments_per_month: int
    planned_clinical_hours_per_month: float

    component_costs_aud: dict[str, float | None]
    total_operational_cost_aud: float | None

    cost_completeness: str
    unknown_cost_components: list[str]
    evidence_statuses: dict[str, str]

    def to_dict(self):
        return asdict(self)


def assess_operational_costs(
    costs: list[OperationalCost],
    service_type: str,
    planned_schedule: PlannedServiceSchedule,
) -> OperationalCostAssessment:
    """Calculate costs using an explicitly validated planned schedule.

    All six cost components must be explicitly declared.
    Unknown costs remain unknown and prevent calculation of a
    complete total.

    This function does not assess funding sufficiency.
    """

    if not isinstance(costs, list):
        raise TypeError("costs must be a list.")

    if not costs:
        raise ValueError("At least one operational cost is required.")

    if service_type not in SERVICE_TYPES:
        raise ValueError(f"Invalid service type: {service_type}")

    if not isinstance(planned_schedule, PlannedServiceSchedule):
        raise TypeError(
            "planned_schedule must be a PlannedServiceSchedule."
        )

    planned_schedule.validate()

    if planned_schedule.service_type != service_type:
        raise ValueError(
            "Planned schedule must match the selected service type."
        )

    trips = planned_schedule.planned_trips_per_month
    appointments = planned_schedule.planned_appointments_per_month
    clinical_hours = planned_schedule.planned_clinical_hours_per_month

    for cost in costs:
        if not isinstance(cost, OperationalCost):
            raise TypeError(
                "Every cost entry must be an OperationalCost instance."
            )
        cost.validate()

        if cost.service_type != service_type:
            raise ValueError(
                "All cost entries must match the selected service type."
            )

    cost_by_component = {}

    for cost in costs:
        if cost.cost_component in cost_by_component:
            raise ValueError(
                f"Duplicate cost component: {cost.cost_component}"
            )
        cost_by_component[cost.cost_component] = cost

    missing_components = COST_COMPONENT_TYPES - set(cost_by_component)

    if missing_components:
        raise ValueError(
            "Missing explicit cost components: "
            + ", ".join(sorted(missing_components))
        )

    quantities = {
        "clinician_labour_per_hour": clinical_hours,
        "travel_per_trip": trips,
        "equipment_per_appointment": appointments,
        "consumables_per_appointment": appointments,
        "other_per_trip": trips,
        "other_per_appointment": appointments,
    }

    component_costs = {}
    evidence_statuses = {}
    unknown_components = []

    for component in sorted(COST_COMPONENT_TYPES):
        cost = cost_by_component[component]
        evidence_statuses[component] = cost.evidence_status

        if cost.amount_aud is None:
            component_costs[component] = None
            unknown_components.append(component)
        else:
            component_costs[component] = (
                cost.amount_aud * quantities[component]
            )

    if unknown_components:
        total_cost = None
        completeness = "incomplete"
    else:
        total_cost = sum(component_costs.values())
        completeness = "complete"

    return OperationalCostAssessment(
        service_type=service_type,
        planned_trips_per_month=trips,
        planned_appointments_per_month=appointments,
        planned_clinical_hours_per_month=clinical_hours,
        component_costs_aud=component_costs,
        total_operational_cost_aud=total_cost,
        cost_completeness=completeness,
        unknown_cost_components=unknown_components,
        evidence_statuses=evidence_statuses,
    )
