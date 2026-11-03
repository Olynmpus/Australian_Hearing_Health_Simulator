"""Simple records of an individual's hearing-care journey."""

from dataclasses import dataclass, field


JOURNEY_STATUSES = {
    "not_started",
    "active",
    "paused",
    "completed",
    "discontinued",
    "unknown",
}

EVENT_EVIDENCE_STATUSES = {
    "policy_supported",
    "user_reported",
    "simulation_assumption",
    "unknown",
}


@dataclass
class JourneyEvent:
    """One recorded event in an individual's hearing-care journey."""

    month: int
    event_type: str
    description: str
    evidence_status: str = "unknown"

    def validate(self):
        if (
            isinstance(self.month, bool)
            or not isinstance(self.month, int)
            or self.month < 0
        ):
            raise ValueError("month must be a non-negative integer.")

        if not isinstance(self.event_type, str) or not self.event_type.strip():
            raise ValueError("event_type must be a non-empty string.")

        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be a non-empty string.")

        if self.evidence_status not in EVENT_EVIDENCE_STATUSES:
            raise ValueError(
                f"Invalid event evidence status: {self.evidence_status}"
            )

        return True

    def to_dict(self):
        self.validate()

        return {
            "month": self.month,
            "event_type": self.event_type,
            "description": self.description,
            "evidence_status": self.evidence_status,
        }


@dataclass
class HearingCareJourney:
    """Current status and recorded events for one care journey."""

    agent_id: str
    journey_id: str
    status: str = "not_started"
    events: list[JourneyEvent] = field(default_factory=list)

    def validate(self):
        if not isinstance(self.agent_id, str) or not self.agent_id.strip():
            raise ValueError("agent_id must be a non-empty string.")

        if not isinstance(self.journey_id, str) or not self.journey_id.strip():
            raise ValueError("journey_id must be a non-empty string.")

        if self.status not in JOURNEY_STATUSES:
            raise ValueError(f"Invalid journey status: {self.status}")

        if not isinstance(self.events, list):
            raise ValueError("events must be a list.")

        for event in self.events:
            if not isinstance(event, JourneyEvent):
                raise ValueError("Every event must be a JourneyEvent.")

            event.validate()

        return True

    def add_event(self, event):
        """Append an event without automatically changing journey status."""

        if not isinstance(event, JourneyEvent):
            raise ValueError("event must be a JourneyEvent.")

        event.validate()
        self.events.append(event)

    def set_status(self, status):
        """Set the current journey status explicitly."""

        if status not in JOURNEY_STATUSES:
            raise ValueError(f"Invalid journey status: {status}")

        self.status = status

    def to_dict(self):
        self.validate()

        ordered_events = sorted(
            self.events,
            key=lambda event: event.month,
        )

        return {
            "agent_id": self.agent_id,
            "journey_id": self.journey_id,
            "status": self.status,
            "events": [
                event.to_dict()
                for event in ordered_events
            ],
        }