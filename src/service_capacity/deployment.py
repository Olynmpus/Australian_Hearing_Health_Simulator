"""Deployment arrangements for mobile hearing services."""

from dataclasses import dataclass
import math

from src.hearing_support.service_access import SERVICE_TYPES
from .constants import AGE_GROUPS
from .funding import EVIDENCE_STATUSES


@dataclass
class MobileServiceDeployment:
    """Describes a mobile service deployment to one destination.

    Service delivery hours are explicitly declared hours available for
    appointments at the destination, excluding travel time.

    This model calculates theoretical appointments per trip. It does not
    imply bookings, attendance or completed appointments.
    """

    deployment_id: str
    service_id: str
    route_id: str
    service_types: list[str]
    target_age_groups: list[str]
    service_delivery_hours_per_trip: float
    evidence_status: str

    def validate(self):
        for field_name in (
            "deployment_id",
            "service_id",
            "route_id",
        ):
            value = getattr(self, field_name)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

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
            not isinstance(self.target_age_groups, list)
            or not self.target_age_groups
        ):
            raise ValueError(
                "target_age_groups must be a non-empty list."
            )

        if not all(
            isinstance(item, str) and item in AGE_GROUPS
            for item in self.target_age_groups
        ):
            raise ValueError("Invalid target age group.")

        if len(self.target_age_groups) != len(
            set(self.target_age_groups)
        ):
            raise ValueError(
                "Duplicate target age groups are not allowed."
            )

        hours = self.service_delivery_hours_per_trip

        if (
            isinstance(hours, bool)
            or not isinstance(hours, (int, float))
            or not math.isfinite(hours)
            or hours <= 0
        ):
            raise ValueError(
                "service_delivery_hours_per_trip must be a finite, "
                "positive number."
            )

        if (
            not isinstance(self.evidence_status, str)
            or self.evidence_status not in EVIDENCE_STATUSES
        ):
            raise ValueError(
                f"Invalid evidence status: {self.evidence_status}"
            )

        return True

    def calculate_appointments_per_trip(
        self,
        appointment_duration_minutes,
    ):
        """Calculate theoretical whole appointments per trip."""

        self.validate()

        if (
            isinstance(appointment_duration_minutes, bool)
            or not isinstance(appointment_duration_minutes, int)
            or appointment_duration_minutes <= 0
        ):
            raise ValueError(
                "appointment_duration_minutes must be a positive integer."
            )

        available_minutes = (
            self.service_delivery_hours_per_trip * 60
        )

        return math.floor(
            available_minutes / appointment_duration_minutes
        )

    def to_dict(self):
        self.validate()

        return {
            "deployment_id": self.deployment_id,
            "service_id": self.service_id,
            "route_id": self.route_id,
            "service_types": list(self.service_types),
            "target_age_groups": list(self.target_age_groups),
            "service_delivery_hours_per_trip": (
                self.service_delivery_hours_per_trip
            ),
            "evidence_status": self.evidence_status,
        }
