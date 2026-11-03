"""Records explicit individual requests and referrals for hearing services."""

from dataclasses import asdict, dataclass

from src.hearing_support.service_access import (
    EVIDENCE_STATUSES,
    SERVICE_TYPES,
)


REQUEST_SOURCES = {
    "individual_request",
    "referral",
}


@dataclass
class ServiceDemand:
    """An independently identifiable request for a hearing-care service."""

    demand_id: str
    agent_id: str
    service_type: str
    request_month: int
    request_source: str
    evidence_status: str = "unknown"

    def validate(self):
        for field_name in ("demand_id", "agent_id"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

        if self.service_type not in SERVICE_TYPES:
            raise ValueError(
                f"Invalid service type: {self.service_type}"
            )

        if (
            isinstance(self.request_month, bool)
            or not isinstance(self.request_month, int)
            or self.request_month < 0
        ):
            raise ValueError(
                "request_month must be a non-negative integer."
            )

        if self.request_source not in REQUEST_SOURCES:
            raise ValueError(
                f"Invalid request source: {self.request_source}"
            )

        if self.evidence_status not in EVIDENCE_STATUSES:
            raise ValueError(
                f"Invalid evidence status: {self.evidence_status}"
            )

        return True

    def to_dict(self):
        self.validate()
        return asdict(self)
