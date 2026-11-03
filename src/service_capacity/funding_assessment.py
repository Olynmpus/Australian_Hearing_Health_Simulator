"""Assessment of operational funding against estimated service costs."""

from dataclasses import asdict, dataclass

from .funding import OperationalFunding
from .cost_assessment import OperationalCostAssessment
from src.hearing_support.service_access import SERVICE_TYPES


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
    funding_ids: list[str]
    funding_evidence_statuses: dict[str, str]
    cost_completeness: str
    operating_schedule_assumption: str
    reasons: list[str]

    def to_dict(self):
        return asdict(self)


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

    matching_records = [
        record
        for record in funding_records
        if service_type in record.service_types
        and geography in record.target_geographies
    ]

    reasons = []

    mismatched_records = [
        record.funding_id
        for record in funding_records
        if record not in matching_records
    ]

    if mismatched_records:
        reasons.append(
            "Funding records excluded because their declared "
            "service or geographic scope does not match: "
            + ", ".join(mismatched_records)
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
            funding_ids=[record.funding_id for record in matching_records],
            funding_evidence_statuses={
                record.funding_id: record.evidence_status
                for record in matching_records
            },
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
            funding_ids=[],
            funding_evidence_statuses={},
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
            funding_ids=[record.funding_id for record in matching_records],
            funding_evidence_statuses={
                record.funding_id: record.evidence_status
                for record in matching_records
            },
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

    if any(
        record.evidence_status in {"simulation_assumption", "unknown"}
        for record in matching_records
    ):
        reasons.append(
            "Funding includes assumptions or unknown evidence status."
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
        funding_ids=[record.funding_id for record in matching_records],
        funding_evidence_statuses={
            record.funding_id: record.evidence_status
            for record in matching_records
        },
        cost_completeness=cost_assessment.cost_completeness,
        operating_schedule_assumption=(
            "Monthly delivery schedule assumed to repeat "
            "unchanged across the operating period."
        ),
        reasons=reasons,
    )
