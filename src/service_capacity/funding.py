"""Government and organisational funding for hearing service operations."""

from dataclasses import dataclass
import math

from src.hearing_support.service_access import SERVICE_TYPES


GEOGRAPHIES = {
    "metropolitan",
    "regional",
    "remote_very_remote",
}

EVIDENCE_STATUSES = {
    "policy_supported",
    "user_reported",
    "simulation_assumption",
    "unknown",
}


@dataclass
class OperationalFunding:
    """Records an operational funding allocation for a hearing service.

    The amount represents funding available to operate services over the
    declared period. It is not an individual subsidy or patient contribution.

    This record does not calculate service costs or appointment capacity.
    """

    funding_id: str
    funding_source: str
    funding_program: str
    available_amount_aud: float
    period_months: int
    service_types: list[str]
    target_geographies: list[str]
    evidence_status: str

    def validate(self):
        for field_name in (
            "funding_id",
            "funding_source",
            "funding_program",
        ):
            value = getattr(self, field_name)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

        amount = self.available_amount_aud

        if (
            isinstance(amount, bool)
            or not isinstance(amount, (int, float))
            or not math.isfinite(amount)
            or amount < 0
        ):
            raise ValueError(
                "available_amount_aud must be a finite, "
                "non-negative number."
            )

        if (
            isinstance(self.period_months, bool)
            or not isinstance(self.period_months, int)
            or self.period_months <= 0
        ):
            raise ValueError("period_months must be a positive integer.")

        if (
            not isinstance(self.service_types, list)
            or not self.service_types
        ):
            raise ValueError("service_types must be a non-empty list.")

        if not all(
            isinstance(item, str) and item in SERVICE_TYPES
            for item in self.service_types
        ):
            raise ValueError("Invalid service type.")

        if len(self.service_types) != len(set(self.service_types)):
            raise ValueError("Duplicate service types are not allowed.")

        if (
            not isinstance(self.target_geographies, list)
            or not self.target_geographies
        ):
            raise ValueError(
                "target_geographies must be a non-empty list."
            )

        if not all(
            isinstance(item, str) and item in GEOGRAPHIES
            for item in self.target_geographies
        ):
            raise ValueError("Invalid target geography.")

        if len(self.target_geographies) != len(
            set(self.target_geographies)
        ):
            raise ValueError(
                "Duplicate target geographies are not allowed."
            )

        if (
            not isinstance(self.evidence_status, str)
            or self.evidence_status not in EVIDENCE_STATUSES
        ):
            raise ValueError(
                f"Invalid evidence status: {self.evidence_status}"
            )

        return True

    def to_dict(self):
        self.validate()

        return {
            "funding_id": self.funding_id,
            "funding_source": self.funding_source,
            "funding_program": self.funding_program,
            "available_amount_aud": self.available_amount_aud,
            "period_months": self.period_months,
            "service_types": list(self.service_types),
            "target_geographies": list(self.target_geographies),
            "evidence_status": self.evidence_status,
        }
