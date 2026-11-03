"""Recorded hearing-support needs and help-seeking information."""

from dataclasses import dataclass
import math


FUNCTIONAL_DIFFICULTY_STATUSES = {
    "no_identified_difficulty",
    "difficulty_reported",
    "functional_difficulty_confirmed",
    "unknown",
}

YES_NO_UNKNOWN = {
    "yes",
    "no",
    "unknown",
}

HELP_SEEKING_ACTIONS = {
    "no_action",
    "information_sought",
    "service_contacted",
    "referral_requested",
    "unknown",
}

EVIDENCE_STATUSES = {
    "policy_supported",
    "user_reported",
    "simulation_assumption",
    "unknown",
}


@dataclass
class HearingSupportNeed:
    """A time-specific record of an individual's support needs.

    This class records information. It does not determine clinical need,
    eligibility, service suitability or treatment recommendations.
    """

    agent_id: str
    assessment_month: int

    functional_difficulty_status: str = "unknown"
    perceived_need: str = "unknown"
    help_seeking_intention: str = "unknown"
    help_seeking_action: str = "unknown"

    evidence_status: str = "unknown"

    def validate(self):
        """Validate the recorded information."""

        if not isinstance(self.agent_id, str) or not self.agent_id.strip():
            raise ValueError("agent_id must be a non-empty string.")

        if (
            not isinstance(self.assessment_month, int)
            or isinstance(self.assessment_month, bool)
            or self.assessment_month < 0
        ):
            raise ValueError(
                "assessment_month must be a non-negative integer."
            )

        if self.functional_difficulty_status not in (
            FUNCTIONAL_DIFFICULTY_STATUSES
        ):
            raise ValueError(
                "Invalid functional_difficulty_status."
            )

        if self.perceived_need not in YES_NO_UNKNOWN:
            raise ValueError("Invalid perceived_need.")

        if self.help_seeking_intention not in YES_NO_UNKNOWN:
            raise ValueError("Invalid help_seeking_intention.")

        if self.help_seeking_action not in HELP_SEEKING_ACTIONS:
            raise ValueError("Invalid help_seeking_action.")

        if self.evidence_status not in EVIDENCE_STATUSES:
            raise ValueError("Invalid evidence_status.")

        return True

    def to_dict(self):
        """Return a serialisable representation of the record."""

        self.validate()

        return {
            "agent_id": self.agent_id,
            "assessment_month": self.assessment_month,
            "functional_difficulty_status": (
                self.functional_difficulty_status
            ),
            "perceived_need": self.perceived_need,
            "help_seeking_intention": self.help_seeking_intention,
            "help_seeking_action": self.help_seeking_action,
            "evidence_status": self.evidence_status,
        }
