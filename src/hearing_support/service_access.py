"""Records an individual's access to hearing-care services."""

from dataclasses import dataclass
from typing import Optional


SERVICE_TYPES = {
    "audiology_assessment",
    "hearing_aid_fitting",
    "cochlear_implant_assessment",
    "rehabilitation",
    "communication_support",
    "other",
    "unknown",
}

SERVICE_PATHWAYS = {
    "public",
    "private",
    "community",
    "mixed",
    "unknown",
}

AVAILABILITY_STATUSES = {
    "available",
    "unavailable",
    "unknown",
}

APPOINTMENT_STATUSES = {
    "not_requested",
    "requested",
    "scheduled",
    "not_available",
    "cancelled",
    "unknown",
}

ATTENDANCE_STATUSES = {
    "not_yet_due",
    "attended",
    "did_not_attend",
    "unknown",
}

EVIDENCE_STATUSES = {
    "policy_supported",
    "user_reported",
    "simulation_assumption",
    "unknown",
}


@dataclass
class ServiceAccess:
    """Records access to one type of hearing-care service."""

    agent_id: str
    service_type: str = "unknown"
    pathway: str = "unknown"
    availability_status: str = "unknown"
    appointment_status: str = "unknown"
    attendance_status: str = "unknown"
    waiting_time_days: Optional[int] = None
    evidence_status: str = "unknown"

    def validate(self):
        if not isinstance(self.agent_id, str) or not self.agent_id.strip():
            raise ValueError("agent_id must be a non-empty string.")

        if self.service_type not in SERVICE_TYPES:
            raise ValueError(
                f"Invalid service type: {self.service_type}"
            )

        if self.pathway not in SERVICE_PATHWAYS:
            raise ValueError(
                f"Invalid service pathway: {self.pathway}"
            )

        if self.availability_status not in AVAILABILITY_STATUSES:
            raise ValueError(
                f"Invalid availability status: {self.availability_status}"
            )

        if self.appointment_status not in APPOINTMENT_STATUSES:
            raise ValueError(
                f"Invalid appointment status: {self.appointment_status}"
            )

        if self.attendance_status not in ATTENDANCE_STATUSES:
            raise ValueError(
                f"Invalid attendance status: {self.attendance_status}"
            )

        if self.evidence_status not in EVIDENCE_STATUSES:
            raise ValueError(
                f"Invalid evidence status: {self.evidence_status}"
            )

        if self.waiting_time_days is not None:
            if (
                isinstance(self.waiting_time_days, bool)
                or not isinstance(self.waiting_time_days, int)
                or self.waiting_time_days < 0
            ):
                raise ValueError(
                    "waiting_time_days must be a non-negative integer or None."
                )

        return True

    def to_dict(self):
        self.validate()

        return {
            "agent_id": self.agent_id,
            "service_type": self.service_type,
            "pathway": self.pathway,
            "availability_status": self.availability_status,
            "appointment_status": self.appointment_status,
            "attendance_status": self.attendance_status,
            "waiting_time_days": self.waiting_time_days,
            "evidence_status": self.evidence_status,
        }