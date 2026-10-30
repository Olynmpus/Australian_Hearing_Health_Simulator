"""Illustrative rules for changes in individual relationships."""

RELATIONSHIP_EFFECTS = {
    "negative_communication": {
        "trust": -0.05,
        "perceived_support": -0.05,
    },
    "misdirected_information": {
        "trust": -0.05,
        "perceived_support": -0.02,
    },
    "supportive_communication": {
        "trust": 0.05,
        "perceived_support": 0.10,
    },
    "successful_service_interaction": {
        "trust": 0.10,
        "perceived_support": 0.05,
    },
    "blocked_service_access": {
        "trust": -0.05,
        "perceived_support": -0.05,
    },
}


def apply_relationship_experience(relationship, outcome):
    """Update one relationship following an interaction.

    These are provisional experimental parameters, not empirical estimates.
    """

    if outcome not in RELATIONSHIP_EFFECTS:
        raise ValueError(f"Unknown relationship outcome: {outcome}")

    changes = RELATIONSHIP_EFFECTS[outcome]
    applied_changes = {}

    for field_name, delta in changes.items():
        old_value = getattr(relationship, field_name)
        new_value = max(0.0, min(1.0, old_value + delta))

        setattr(relationship, field_name, new_value)

        applied_changes[field_name] = {
            "before": old_value,
            "after": new_value,
            "requested_change": delta,
        }

    relationship.validate()

    return applied_changes
