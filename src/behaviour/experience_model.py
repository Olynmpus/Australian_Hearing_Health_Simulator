"""Transparent, illustrative rules for updating agent state."""

from dataclasses import fields


# These are provisional simulation parameters, not empirical estimates.
EXPERIENCE_EFFECTS = {
    "negative_communication": {
        "communication_confidence": -0.05,
        "social_participation": -0.03,
        "frustration": 0.10,
    },
    "misdirected_information": {
        "trust_in_services": -0.10,
        "frustration": 0.10,
    },
    "supportive_communication": {
        "communication_confidence": 0.05,
        "social_participation": 0.05,
        "perceived_support": 0.05,
        "frustration": -0.05,
    },
    "successful_service_interaction": {
        "trust_in_services": 0.10,
        "help_seeking_intention": 0.05,
        "frustration": -0.05,
    },
    "blocked_service_access": {
        "trust_in_services": -0.05,
        "help_seeking_intention": -0.05,
        "frustration": 0.10,
    },
}


def apply_experience(state, outcome):
    """Apply one explicitly defined experience to an agent's state.

    Values are bounded between 0 and 1.
    Returns the changes that were applied.
    """

    if outcome not in EXPERIENCE_EFFECTS:
        raise ValueError(f"Unknown experience outcome: {outcome}")

    changes = EXPERIENCE_EFFECTS[outcome]

    valid_fields = {item.name for item in fields(state)}

    for field_name in changes:
        if field_name not in valid_fields:
            raise ValueError(f"Unknown agent state field: {field_name}")

    applied_changes = {}

    for field_name, delta in changes.items():
        old_value = getattr(state, field_name)
        new_value = max(0.0, min(1.0, old_value + delta))

        setattr(state, field_name, new_value)
        applied_changes[field_name] = {
            "before": old_value,
            "after": new_value,
            "requested_change": delta,
        }

    state.validate()

    return applied_changes
