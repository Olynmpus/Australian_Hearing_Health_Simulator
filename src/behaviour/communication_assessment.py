
"""Transparent assessment of communication conditions.

All calculation parameters in this initial version are illustrative
simulation assumptions, not validated clinical measurements.
"""


def assess_acoustic_conditions(environment, channel):
    """Estimate environmental conditions for speech communication.

    Returns an indicator between 0 and 1 for speech.
    Returns None when acoustic conditions are not applicable.
    """

    environment.validate()

    if channel != "speech":
        return None

    # Illustrative distance factors, not empirical estimates.
    if environment.distance_metres <= 1:
        distance_factor = 1.0
    elif environment.distance_metres >= 10:
        distance_factor = 0.0
    else:
        distance_factor = 1.0 - (
            (environment.distance_metres - 1) / 10
        )

    indicator = (
        environment.message_clarity
        * (1 - environment.background_noise)
        * distance_factor
    )

    return max(0.0, min(1.0, indicator))


def assess_visual_support(environment):
    """Record the visual and written supports available.

    These are environmental observations, not measures of
    comprehension or individual communication ability.
    """

    environment.validate()

    return {
        "face_visible": environment.speaker_face_visible,
        "written_information_available": (
            environment.written_information_available
        ),
    }
