"""Clinical workforce availability and theoretical appointment capacity."""

from dataclasses import dataclass
import math

from src.hearing_support.service_access import SERVICE_TYPES
from .constants import AGE_GROUPS
from .funding import EVIDENCE_STATUSES


CLINICAL_ROLES = {
    "audiologist",
    "audiology_assistant",
    "other_clinician",
    "support_worker",
}


@dataclass
class WorkforceMember:
    """Represents one clinical or support workforce member.

    Available clinical hours are direct service-delivery hours per month,
    after administration, breaks and other non-clinical duties.

    Service types and supported age groups must be explicitly declared.
    Neither is inferred from job title or qualifications.
    """

    clinician_id: str
    role: str
    qualifications: list[str]
    service_types: list[str]
    supported_age_groups: list[str]
    available_clinical_hours_per_month: float
    appointment_duration_minutes: int
    evidence_status: str

    def validate(self):
        if (
            not isinstance(self.clinician_id, str)
            or not self.clinician_id.strip()
        ):
            raise ValueError("clinician_id must be a non-empty string.")

        if not isinstance(self.role, str) or self.role not in CLINICAL_ROLES:
            raise ValueError(f"Invalid clinical role: {self.role}")

        if not isinstance(self.qualifications, list) or not self.qualifications:
            raise ValueError("qualifications must be a non-empty list.")

        if not all(
            isinstance(item, str) and item.strip()
            for item in self.qualifications
        ):
            raise ValueError(
                "Each qualification must be a non-empty string."
            )

        if not isinstance(self.service_types, list) or not self.service_types:
            raise ValueError("service_types must be a non-empty list.")

        if not all(
            isinstance(item, str) and item in SERVICE_TYPES
            for item in self.service_types
        ):
            raise ValueError("Invalid service type.")

        if len(self.service_types) != len(set(self.service_types)):
            raise ValueError("Duplicate service types are not allowed.")

        if (
            not isinstance(self.supported_age_groups, list)
            or not self.supported_age_groups
        ):
            raise ValueError(
                "supported_age_groups must be a non-empty list."
            )

        if not all(
            isinstance(item, str) and item in AGE_GROUPS
            for item in self.supported_age_groups
        ):
            raise ValueError("Invalid supported age group.")

        if len(self.supported_age_groups) != len(
            set(self.supported_age_groups)
        ):
            raise ValueError(
                "Duplicate supported age groups are not allowed."
            )

        hours = self.available_clinical_hours_per_month

        if (
            isinstance(hours, bool)
            or not isinstance(hours, (int, float))
            or not math.isfinite(hours)
            or hours < 0
        ):
            raise ValueError(
                "available_clinical_hours_per_month must be "
                "a finite, non-negative number."
            )

        duration = self.appointment_duration_minutes

        if (
            isinstance(duration, bool)
            or not isinstance(duration, int)
            or duration <= 0
        ):
            raise ValueError(
                "appointment_duration_minutes must be a positive integer."
            )

        if (
            not isinstance(self.evidence_status, str)
            or self.evidence_status not in EVIDENCE_STATUSES
        ):
            raise ValueError(
                f"Invalid evidence status: {self.evidence_status}"
            )

        return True

    def supports_age_group(self, age_group):
        """Check explicitly declared workforce age-group scope."""

        self.validate()

        if not isinstance(age_group, str) or age_group not in AGE_GROUPS:
            raise ValueError(f"Invalid age group: {age_group}")

        return age_group in self.supported_age_groups

    def calculate_monthly_appointment_capacity(self, service_type):
        """Calculate theoretical capacity for a declared service.

        This calculation does not apply age-group restrictions.
        """

        self.validate()

        if service_type not in SERVICE_TYPES:
            raise ValueError(f"Invalid service type: {service_type}")

        if service_type not in self.service_types:
            return 0

        available_minutes = (
            self.available_clinical_hours_per_month * 60
        )

        return math.floor(
            available_minutes / self.appointment_duration_minutes
        )

    def calculate_monthly_appointment_capacity_for_age_group(
        self,
        service_type,
        age_group,
    ):
        """Calculate capacity when both service and age scope are declared."""

        self.validate()

        if service_type not in SERVICE_TYPES:
            raise ValueError(f"Invalid service type: {service_type}")

        if not isinstance(age_group, str) or age_group not in AGE_GROUPS:
            raise ValueError(f"Invalid age group: {age_group}")

        if (
            service_type not in self.service_types
            or age_group not in self.supported_age_groups
        ):
            return 0

        return self.calculate_monthly_appointment_capacity(service_type)

    def to_dict(self):
        self.validate()

        return {
            "clinician_id": self.clinician_id,
            "role": self.role,
            "qualifications": list(self.qualifications),
            "service_types": list(self.service_types),
            "supported_age_groups": list(self.supported_age_groups),
            "available_clinical_hours_per_month": (
                self.available_clinical_hours_per_month
            ),
            "appointment_duration_minutes": (
                self.appointment_duration_minutes
            ),
            "evidence_status": self.evidence_status,
        }
