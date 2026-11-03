"""Declared age-group suitability for hearing services."""

from dataclasses import dataclass

from src.hearing_support.service_access import SERVICE_TYPES
from .funding import EVIDENCE_STATUSES


from .constants import AGE_GROUPS

SUITABILITY_STATUSES = {
    "suitable",
    "not_suitable",
    "assessment_required",
    "unknown",
}


@dataclass
class AgeServiceSuitability:
    """Records a declared suitability assessment for an age group.

    This is a service-level declaration, not an individual clinical
    assessment or a guarantee that every person in the age group
    is suitable for the service.

    Requirements and limitations must be explicitly supplied.
    No suitability is inferred from age or service type.
    """

    age_group: str
    service_type: str
    suitability_status: str
    requirements: list[str]
    limitations: list[str]
    evidence_status: str

    def validate(self):
        if (
            not isinstance(self.age_group, str)
            or self.age_group not in AGE_GROUPS
        ):
            raise ValueError(f"Invalid age group: {self.age_group}")

        if (
            not isinstance(self.service_type, str)
            or self.service_type not in SERVICE_TYPES
        ):
            raise ValueError(f"Invalid service type: {self.service_type}")

        if (
            not isinstance(self.suitability_status, str)
            or self.suitability_status not in SUITABILITY_STATUSES
        ):
            raise ValueError(
                f"Invalid suitability status: {self.suitability_status}"
            )

        for field_name in ("requirements", "limitations"):
            values = getattr(self, field_name)

            if not isinstance(values, list):
                raise ValueError(f"{field_name} must be a list.")

            if not all(
                isinstance(item, str) and item.strip()
                for item in values
            ):
                raise ValueError(
                    f"Each {field_name} entry must be a non-empty string."
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
            "age_group": self.age_group,
            "service_type": self.service_type,
            "suitability_status": self.suitability_status,
            "requirements": list(self.requirements),
            "limitations": list(self.limitations),
            "evidence_status": self.evidence_status,
        }
