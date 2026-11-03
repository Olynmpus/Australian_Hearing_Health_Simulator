"""Integrated assessment of mobile hearing service capacity."""

from dataclasses import asdict, dataclass

from .age_suitability import AgeServiceSuitability
from .deployment import MobileServiceDeployment
from .geographic_access import GeographicRoute
from .workforce import WorkforceMember


@dataclass
class ServiceCapacityAssessment:
    """Structured result of a mobile service capacity assessment."""

    service_id: str
    service_type: str
    age_group: str

    workforce_service_capacity_per_month: int
    workforce_service_scope_supported: bool
    workforce_age_scope_supported: bool

    deployment_service_supported: bool
    deployment_age_group_supported: bool

    trips_per_month: int
    appointments_per_trip: int
    travel_supported_appointments_per_month: int

    suitability_status: str
    scope_eligible_workforce_capacity_per_month: int
    deliverable_capacity_per_month: int

    assessment_status: str
    limiting_constraints: list[str]
    reasons: list[str]

    funding_status: str = "not_calculated"

    def to_dict(self):
        """Return a serialisable assessment result."""
        return asdict(self)


def assess_mobile_service_capacity(
    workforce: WorkforceMember,
    route: GeographicRoute,
    deployment: MobileServiceDeployment,
    suitability: AgeServiceSuitability,
    service_type: str,
    age_group: str,
) -> ServiceCapacityAssessment:
    """Assess one member, route, service type and age group.

    Reports theoretical workforce and travel capacity separately.
    Deliverable capacity is only calculated when all declared scope
    and suitability conditions are satisfied.

    Funding, bookings, attendance and completed appointments are
    outside the scope of this assessment.
    """

    expected_types = (
        (workforce, WorkforceMember, "workforce"),
        (route, GeographicRoute, "route"),
        (deployment, MobileServiceDeployment, "deployment"),
        (suitability, AgeServiceSuitability, "suitability"),
    )

    for value, expected_type, name in expected_types:
        if not isinstance(value, expected_type):
            raise TypeError(
                f"{name} must be a {expected_type.__name__} instance."
            )

    workforce.validate()
    route.validate()
    deployment.validate()
    suitability.validate()

    if route.service_id != deployment.service_id:
        raise ValueError(
            "Geographic route and deployment must reference "
            "the same service_id."
        )

    if route.route_id != deployment.route_id:
        raise ValueError(
            "Geographic route and deployment must reference "
            "the same route_id."
        )

    if suitability.service_type != service_type:
        raise ValueError(
            "Suitability record does not match the selected service type."
        )

    if suitability.age_group != age_group:
        raise ValueError(
            "Suitability record does not match the selected age group."
        )

    workforce_service_supported = service_type in workforce.service_types
    workforce_age_supported = workforce.supports_age_group(age_group)

    deployment_service_supported = service_type in deployment.service_types
    deployment_age_supported = age_group in deployment.target_age_groups

    # Theoretical workforce capacity for the selected service.
    workforce_capacity = (
        workforce.calculate_monthly_appointment_capacity(service_type)
    )

    # Theoretical travel capacity, retained even when scope checks fail.
    trips_per_month = route.calculate_monthly_trip_capacity()

    appointments_per_trip = deployment.calculate_appointments_per_trip(
        workforce.appointment_duration_minutes
    )

    travel_capacity = trips_per_month * appointments_per_trip

    scope_supported = (
        workforce_service_supported
        and workforce_age_supported
        and deployment_service_supported
        and deployment_age_supported
    )

    scope_eligible_workforce_capacity = (
        workforce_capacity if scope_supported else 0
    )

    suitability_status = suitability.suitability_status

    reasons = []
    blocking_constraints = []

    if not workforce_service_supported:
        reasons.append(
            "Workforce member is not declared to provide this service."
        )

    if not workforce_age_supported:
        reasons.append(
            "Workforce member is not declared to support this age group."
        )

    if not deployment_service_supported:
        reasons.append(
            "Deployment does not include the selected service."
        )

    if not deployment_age_supported:
        reasons.append(
            "Deployment does not target the selected age group."
        )

    if not scope_supported:
        blocking_constraints.append("scope")

    if suitability_status == "not_suitable":
        reasons.append(
            "The declared service suitability is not suitable "
            "for this age group."
        )
    elif suitability_status == "assessment_required":
        reasons.append(
            "Individual assessment is required before suitability "
            "can be established."
        )
    elif suitability_status == "unknown":
        reasons.append(
            "Service suitability for this age group is unknown."
        )

    if suitability_status != "suitable":
        blocking_constraints.append("suitability")

    eligible = not blocking_constraints

    if eligible:
        deliverable_capacity = min(
            workforce_capacity,
            travel_capacity,
        )

        if workforce_capacity < travel_capacity:
            limiting_constraints = ["workforce"]
        elif travel_capacity < workforce_capacity:
            limiting_constraints = ["travel"]
        else:
            limiting_constraints = ["workforce", "travel"]

        if deliverable_capacity == 0:
            assessment_status = "zero_capacity"
            reasons.append(
                "No positive monthly capacity is available under "
                "the declared workforce and travel constraints."
            )
        else:
            assessment_status = "eligible"
    else:
        deliverable_capacity = 0
        limiting_constraints = blocking_constraints
        assessment_status = "restricted"

    return ServiceCapacityAssessment(
        service_id=deployment.service_id,
        service_type=service_type,
        age_group=age_group,
        workforce_service_capacity_per_month=workforce_capacity,
        workforce_service_scope_supported=workforce_service_supported,
        workforce_age_scope_supported=workforce_age_supported,
        deployment_service_supported=deployment_service_supported,
        deployment_age_group_supported=deployment_age_supported,
        trips_per_month=trips_per_month,
        appointments_per_trip=appointments_per_trip,
        travel_supported_appointments_per_month=travel_capacity,
        suitability_status=suitability_status,
        scope_eligible_workforce_capacity_per_month=(
            scope_eligible_workforce_capacity
        ),
        deliverable_capacity_per_month=deliverable_capacity,
        assessment_status=assessment_status,
        limiting_constraints=limiting_constraints,
        reasons=reasons,
    )
