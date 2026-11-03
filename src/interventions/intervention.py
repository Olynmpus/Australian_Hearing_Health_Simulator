"""Definitions and validation for hearing-health interventions."""

from dataclasses import dataclass, field


INTERVENTION_TYPES = {
    "technology",
    "service",
    "public_campaign",
    "policy",
}

GEOGRAPHIES = {
    "metropolitan",
    "regional",
    "remote_very_remote",
}

EVIDENCE_STATUSES = {
    "evidence_supported",
    "simulation_assumption",
    "not_yet_established",
}


@dataclass
class Intervention:
    """Describes a proposed intervention without assuming its effectiveness."""

    intervention_id: str
    name: str
    description: str
    intervention_type: str
    target_geographies: list[str]
    intended_service_change: str
    evidence_status: str
    assumptions: list[str] = field(default_factory=list)

    def validate(self):
        required_strings = {
            "intervention_id": self.intervention_id,
            "name": self.name,
            "description": self.description,
            "intended_service_change": self.intended_service_change,
            "intervention_type": self.intervention_type,
            "evidence_status": self.evidence_status,
        }

        for field_name, value in required_strings.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

        if self.intervention_type not in INTERVENTION_TYPES:
            raise ValueError(
                f"Invalid intervention type: {self.intervention_type}"
            )

        if self.evidence_status not in EVIDENCE_STATUSES:
            raise ValueError(
                f"Invalid evidence status: {self.evidence_status}"
            )

        if not isinstance(self.target_geographies, list):
            raise ValueError("target_geographies must be a list.")

        if not self.target_geographies:
            raise ValueError(
                "At least one target geography must be specified."
            )

        if not all(
            isinstance(item, str) and item in GEOGRAPHIES
            for item in self.target_geographies
        ):
            raise ValueError("Invalid target geography.")

        if len(self.target_geographies) != len(set(self.target_geographies)):
            raise ValueError("Duplicate target geographies are not allowed.")

        if not isinstance(self.assumptions, list):
            raise ValueError("assumptions must be a list.")

        if not all(
            isinstance(item, str) and item.strip()
            for item in self.assumptions
        ):
            raise ValueError(
                "Each assumption must be a non-empty string."
            )

        return True


    def to_dict(self):
        self.validate()

        return {
            "intervention_id": self.intervention_id,
            "name": self.name,
            "description": self.description,
            "intervention_type": self.intervention_type,
            "target_geographies": list(self.target_geographies),
            "intended_service_change": self.intended_service_change,
            "evidence_status": self.evidence_status,
            "assumptions": list(self.assumptions),
        }
