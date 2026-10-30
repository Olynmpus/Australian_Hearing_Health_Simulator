"""Social relationships between simulated agents."""

from dataclasses import dataclass


@dataclass
class SocialRelationship:
    agent_id: str
    contact_id: str
    relationship_type: str

    trust: float = 0.5
    perceived_support: float = 0.5
    interactions_per_month: float = 1.0

    status: str = "active"

    def validate(self):
        """Validate relationship values."""

        if not self.agent_id or not self.contact_id:
            raise ValueError("Both agent IDs are required.")

        if self.agent_id == self.contact_id:
            raise ValueError("An agent cannot have a relationship with itself.")

        for name in ("trust", "perceived_support"):
            value = getattr(self, name)

            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1.")

        if self.interactions_per_month < 0:
            raise ValueError("Interaction frequency cannot be negative.")

        allowed_statuses = {
            "active",
            "strained",
            "disconnected",
        }

        if self.status not in allowed_statuses:
            raise ValueError(f"Invalid relationship status: {self.status}")
