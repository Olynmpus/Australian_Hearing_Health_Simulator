"""Explicit cost assumptions for hearing service operations."""

from dataclasses import dataclass
import math

from src.hearing_support.service_access import SERVICE_TYPES
from .funding import EVIDENCE_STATUSES


COST_COMPONENT_TYPES = {
    "clinician_labour_per_hour",
    "travel_per_trip",
    "equipment_per_appointment",
    "consumables_per_appointment",
    "other_per_trip",
    "other_per_appointment",
}


@dataclass
class OperationalCost:
    """A declared operational cost component."""

    cost_id: str
    cost_component: str
    service_type: str
    amount_aud: float | None
    evidence_status: str
    description: str

    def validate(self):
        for field_name in ("cost_id", "description"):
            value = getattr(self, field_name)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

        if self.cost_component not in COST_COMPONENT_TYPES:
            raise ValueError(
                f"Invalid cost component: {self.cost_component}"
            )

        if self.service_type not in SERVICE_TYPES:
            raise ValueError(
                f"Invalid service type: {self.service_type}"
            )

        if self.evidence_status not in EVIDENCE_STATUSES:
            raise ValueError(
                f"Invalid evidence status: {self.evidence_status}"
            )

        amount = self.amount_aud

        if self.evidence_status == "unknown":
            if amount is not None:
                raise ValueError(
                    "An unknown cost must have amount_aud=None."
                )
        elif (
            amount is None
            or isinstance(amount, bool)
            or not isinstance(amount, (int, float))
            or not math.isfinite(amount)
            or amount < 0
        ):
            raise ValueError(
                "Known costs require a finite, non-negative amount_aud."
            )

        return True

    def to_dict(self):
        self.validate()

        return {
            "cost_id": self.cost_id,
            "cost_component": self.cost_component,
            "service_type": self.service_type,
            "amount_aud": self.amount_aud,
            "evidence_status": self.evidence_status,
            "description": self.description,
        }
