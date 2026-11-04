"""Recorded funding arrangements for hearing support.

This module stores funding information. It does not determine
eligibility or calculate government entitlements.

All monetary values are recorded in Australian dollars (AUD).
"""

from dataclasses import dataclass
import math
from typing import Optional


FUNDING_PATHWAYS = {
    "public",
    "private",
    "mixed",
    "self_funded",
    "other",
    "unknown",
}

ELIGIBILITY_STATUSES = {
    "eligible",
    "ineligible",
    "pending",
    "unknown",
}

EVIDENCE_STATUSES = {
    "policy_supported",
    "user_reported",
    "simulation_assumption",
    "unknown",
}


@dataclass
class FundingArrangement:
    """Recorded funding arrangement for an individual."""

    agent_id: str

    funding_pathway: str = "unknown"
    eligibility_status: str = "unknown"

    subsidy_amount: float = 0.0
    private_contribution: float = 0.0
    out_of_pocket_cost: float = 0.0

    policy_reference: Optional[str] = None
    policy_version: Optional[str] = None

    evidence_status: str = "unknown"

    def validate(self):
        """Validate funding information without calculating eligibility."""

        if not isinstance(self.agent_id, str) or not self.agent_id.strip():
            raise ValueError("agent_id must be a non-empty string.")

        if self.funding_pathway not in FUNDING_PATHWAYS:
            raise ValueError(
                f"Invalid funding pathway: {self.funding_pathway}"
            )

        if self.eligibility_status not in ELIGIBILITY_STATUSES:
            raise ValueError(
                f"Invalid eligibility status: {self.eligibility_status}"
            )

        if self.evidence_status not in EVIDENCE_STATUSES:
            raise ValueError(
                f"Invalid evidence status: {self.evidence_status}"
            )

        monetary_fields = (
            "subsidy_amount",
            "private_contribution",
            "out_of_pocket_cost",
        )

        for field_name in monetary_fields:
            value = getattr(self, field_name)

            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value < 0
            ):
                raise ValueError(
                    f"{field_name} must be a finite, non-negative "
                    f"monetary amount in AUD."
                )

        for field_name in ("policy_reference", "policy_version"):
            value = getattr(self, field_name)

            if value is not None and (
                not isinstance(value, str) or not value.strip()
            ):
                raise ValueError(
                    f"{field_name} must be a non-empty string or None."
                )

        return True

    def validate_country_pathways(self, country_profile):
        """Validate the funding pathway against a country profile."""
        self.validate()

        if not isinstance(country_profile, dict):
            raise ValueError("country_profile must be a dictionary.")

        healthcare = country_profile.get("healthcare_system")

        if not isinstance(healthcare, dict):
            raise ValueError(
                "Country profile must contain a healthcare_system object."
            )

        pathways = healthcare.get("funding_pathways")

        if (
            not isinstance(pathways, list)
            or not pathways
            or any(
                not isinstance(item, str) or not item.strip()
                for item in pathways
            )
            or len(pathways) != len(set(pathways))
        ):
            raise ValueError(
                "Country funding pathways must be a non-empty "
                "list of unique strings."
            )

        if self.funding_pathway not in pathways:
            raise ValueError(
                f"Funding pathway '{self.funding_pathway}' "
                "is not supported by this country profile."
            )

        return True

    def to_dict(self):
        """Return a serialisable representation of the arrangement."""

        self.validate()

        return {
            "agent_id": self.agent_id,
            "funding_pathway": self.funding_pathway,
            "eligibility_status": self.eligibility_status,
            "subsidy_amount": self.subsidy_amount,
            "private_contribution": self.private_contribution,
            "out_of_pocket_cost": self.out_of_pocket_cost,
            "policy_reference": self.policy_reference,
            "policy_version": self.policy_version,
            "evidence_status": self.evidence_status,
        }
