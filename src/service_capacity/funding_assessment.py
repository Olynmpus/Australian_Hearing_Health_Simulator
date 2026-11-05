
"""Assessment of operational funding against estimated service costs."""

from dataclasses import asdict, dataclass

from .funding import OperationalFunding
from .cost_assessment import OperationalCostAssessment
from src.hearing_support.service_access import SERVICE_TYPES


def _classify_evidence_quality(statuses: list[str]) -> str:
    """Summarise the evidence quality across funding and cost inputs."""

    if not statuses:
        return "unknown"

    unique_statuses = set(statuses)

    if unique_statuses == {"unknown"}:
        return "unknown"

    if "unknown" in unique_statuses:
        return "mixed"

    if "simulation_assumption" in unique_statuses:
        return "simulation_assumption"

    if unique_statuses == {"policy_supported"}:
        return "policy_supported"

    if unique_statuses <= {"policy_supported", "user_reported"}:
        return "user_reported"

    return "mixed"


@dataclass
class FundingAssessment:
    """Funding sufficiency assessment for one service and geography."""

    service_type: str
    geography: str
    operating_months: int

    monthly_operational_cost_aud: float | None
    estimated_operational_cost_aud: float | None
    total_available_funding_aud: float | None
    funding_balance_aud: float | None

    assessment_status: str
    evidence_quality: str
    funding_ids: list[str]
    funding_evidence_statuses: dict[str, str]
    cost_evidence_statuses: dict[str, str]
    cost_completeness: str
    operating_schedule_assumption: str
    reasons: list[str]

    def to_dict(self):
        return asdict(self)

def _validate_funding_relationships(
    funding_records: list[OperationalFunding],
) -> None:
    """Validate parent-child relationships across funding records."""

    records_by_id = {
        record.funding_id: record
        for record in funding_records
    }

    for record in funding_records:
        parent_id = record.parent_funding_id

        if parent_id is not None and parent_id not in records_by_id:
            raise ValueError(
                f"Parent funding record '{parent_id}' "
                f"referenced by '{record.funding_id}' does not exist."
            )

    for record in funding_records:
        visited = set()
        current = record

        while current.parent_funding_id is not None:
            if current.funding_id in visited:
                raise ValueError(
                    "Circular funding relationships detected."
                )

            visited.add(current.funding_id)
            current = records_by_id[current.parent_funding_id]

def assess_operational_funding(
    funding_records: list[OperationalFunding],
    cost_assessment: OperationalCostAssessment,
    service_type: str,
    geography: str,
    operating_months: int,
) -> FundingAssessment:
    """Compare funding with recurring monthly operational costs.

    The monthly cost schedule is assumed to repeat for every
    operating month. This is an explicit simulation assumption.

    Funding periods must match operating_months exactly.
    Monthly funding availability and cashflow are not modelled.
    """

    if not isinstance(funding_records, list):
        raise TypeError("funding_records must be a list.")

    if not funding_records:
        raise ValueError("At least one funding record is required.")

    if not isinstance(cost_assessment, OperationalCostAssessment):
        raise TypeError(
            "cost_assessment must be an OperationalCostAssessment."
        )

    if service_type not in SERVICE_TYPES:
        raise ValueError(f"Invalid service type: {service_type}")

    if geography not in {
        "metropolitan",
        "regional",
        "remote_very_remote",
    }:
        raise ValueError(f"Invalid geography: {geography}")

    if (
        isinstance(operating_months, bool)
        or not isinstance(operating_months, int)
        or operating_months <= 0
    ):
        raise ValueError(
            "operating_months must be a positive integer."
        )

    if cost_assessment.service_type != service_type:
        raise ValueError(
            "Cost assessment service type does not match."
        )

    for record in funding_records:
        if not isinstance(record, OperationalFunding):
            raise TypeError(
                "Every funding record must be an OperationalFunding."
            )
        record.validate()

    funding_ids = [record.funding_id for record in funding_records]

    if len(funding_ids) != len(set(funding_ids)):
        raise ValueError("Duplicate funding IDs are not allowed.")

    _validate_funding_relationships(funding_records)

    scoped_records = [
        record
        for record in funding_records
        if service_type in record.service_types
        and geography in record.target_geographies
    ]

    scoped_funding_ids = {
        record.funding_id for record in scoped_records
    }

    records_by_id = {
        record.funding_id: record
        for record in funding_records
    }

    matching_records = []
    excluded_child_funding_ids = []

    for record in scoped_records:
        ancestor_id = record.parent_funding_id
        has_matching_ancestor = False

        while ancestor_id is not None:
            if ancestor_id in scoped_funding_ids:
                has_matching_ancestor = True
                break

            ancestor_id = records_by_id[
                ancestor_id
            ].parent_funding_id

        if has_matching_ancestor:
            excluded_child_funding_ids.append(record.funding_id)
        else:
            matching_records.append(record)


    reasons = []

    if excluded_child_funding_ids:
        reasons.append(
            "Child funding allocations excluded from aggregation "
            "because their parent allocations are already counted: "
            + ", ".join(excluded_child_funding_ids)
        )

    mismatched_records = [
        record.funding_id
        for record in funding_records
        if record not in scoped_records
    ]

    if mismatched_records:
        reasons.append(
            "Funding records excluded because their declared "
            "service or geographic scope does not match: "
            + ", ".join(mismatched_records)
        )

    funding_evidence_statuses = {
        record.funding_id: record.evidence_status
        for record in matching_records
    }
    cost_evidence_statuses = dict(cost_assessment.evidence_statuses)

    evidence_quality = _classify_evidence_quality(
        list(funding_evidence_statuses.values())
        + list(cost_evidence_statuses.values())
    )

    if any(
        record.period_months != operating_months
        for record in matching_records
    ):
        reasons.append(
            "Funding periods do not match the operating period."
        )

        return FundingAssessment(
            service_type=service_type,
            geography=geography,
            operating_months=operating_months,
            monthly_operational_cost_aud=(
                cost_assessment.total_operational_cost_aud
            ),
            estimated_operational_cost_aud=None,
            total_available_funding_aud=None,
            funding_balance_aud=None,
            assessment_status="not_comparable",
            evidence_quality=evidence_quality,
            funding_ids=[record.funding_id for record in matching_records],
            funding_evidence_statuses=funding_evidence_statuses,
            cost_evidence_statuses=cost_evidence_statuses,
            cost_completeness=cost_assessment.cost_completeness,
            operating_schedule_assumption=(
                "Monthly delivery schedule assumed to repeat "
                "unchanged across the operating period."
            ),
            reasons=reasons,
        )

    if not matching_records:
        reasons.append(
            "No funding records match the requested service and geography."
        )

        return FundingAssessment(
            service_type=service_type,
            geography=geography,
            operating_months=operating_months,
            monthly_operational_cost_aud=(
                cost_assessment.total_operational_cost_aud
            ),
            estimated_operational_cost_aud=None,
            total_available_funding_aud=None,
            funding_balance_aud=None,
            assessment_status="incomplete",
            evidence_quality=evidence_quality,
            funding_ids=[],
            funding_evidence_statuses={},
            cost_evidence_statuses=cost_evidence_statuses,
            cost_completeness=cost_assessment.cost_completeness,
            operating_schedule_assumption=(
                "Monthly delivery schedule assumed to repeat "
                "unchanged across the operating period."
            ),
            reasons=reasons,
        )

    total_funding = sum(
        record.available_amount_aud
        for record in matching_records
    )

    if (
        cost_assessment.total_operational_cost_aud is None
        or cost_assessment.cost_completeness != "complete"
    ):
        reasons.append("Monthly operational cost estimate is incomplete.")

        return FundingAssessment(
            service_type=service_type,
            geography=geography,
            operating_months=operating_months,
            monthly_operational_cost_aud=None,
            estimated_operational_cost_aud=None,
            total_available_funding_aud=total_funding,
            funding_balance_aud=None,
            assessment_status="incomplete",
            evidence_quality=evidence_quality,
            funding_ids=[record.funding_id for record in matching_records],
            funding_evidence_statuses=funding_evidence_statuses,
            cost_evidence_statuses=cost_evidence_statuses,
            cost_completeness=cost_assessment.cost_completeness,
            operating_schedule_assumption=(
                "Monthly delivery schedule assumed to repeat "
                "unchanged across the operating period."
            ),
            reasons=reasons,
        )

    monthly_cost = cost_assessment.total_operational_cost_aud
    total_cost = monthly_cost * operating_months
    balance = total_funding - total_cost

    if balance >= 0:
        status = "sufficient"
        reasons.append(
            "Declared funding covers the estimated operating-period cost."
        )
    else:
        status = "insufficient"
        reasons.append(
            "Declared funding is below the estimated operating-period cost."
        )

    if evidence_quality in {"simulation_assumption", "unknown", "mixed"}:
        reasons.append(
            "The funding or cost calculation includes assumptions, "
            "unknown evidence, or mixed evidence quality."
        )

    return FundingAssessment(
        service_type=service_type,
        geography=geography,
        operating_months=operating_months,
        monthly_operational_cost_aud=monthly_cost,
        estimated_operational_cost_aud=total_cost,
        total_available_funding_aud=total_funding,
        funding_balance_aud=balance,
        assessment_status=status,
        evidence_quality=evidence_quality,
        funding_ids=[record.funding_id for record in matching_records],
        funding_evidence_statuses=funding_evidence_statuses,
        cost_evidence_statuses=cost_evidence_statuses,
        cost_completeness=cost_assessment.cost_completeness,
        operating_schedule_assumption=(
            "Monthly delivery schedule assumed to repeat "
            "unchanged across the operating period."
        ),
        reasons=reasons,
    )
