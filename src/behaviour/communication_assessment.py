
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

# Illustrative simulation assumptions, not validated clinical thresholds.
MAX_BACKGROUND_NOISE_FOR_QUIET = 0.2
MAX_DISTANCE_FOR_CLOSE_COMMUNICATION = 2.0


def assess_communication_compatibility(
    communication_profile,
    environment,
    channel="speech",
    vocabulary=None,
):
    """Compare declared environmental preferences with observed conditions.

    This function assesses environmental compatibility only.
    It does not estimate comprehension or communication success.
    """

    communication_profile.validate(vocabulary)
    environment.validate()

    allowed_channels = {
        "speech", "text", "sign", "visual", "other"
    }

    if channel not in allowed_channels:
        raise ValueError(f"Invalid communication channel: {channel}")

    preferences = communication_profile.environmental_preferences


    results = {}

    for preference in preferences:

        if preference in {
            "quiet_environment",
            "reduced_background_noise",
        }:
            if channel != "speech":
                status = "not_applicable"
                observed_value = None
                threshold = MAX_BACKGROUND_NOISE_FOR_QUIET
            else:
                observed_value = environment.background_noise
                threshold = MAX_BACKGROUND_NOISE_FOR_QUIET

                status = (
                    "met"
                    if observed_value <= threshold
                    else "not_met"
                )

        elif preference == "close_speaker_distance":
            observed_value = environment.distance_metres
            threshold = MAX_DISTANCE_FOR_CLOSE_COMMUNICATION

            status = (
                "met"
                if observed_value <= threshold
                else "not_met"
            )

        else:
            status = "not_assessed"
            observed_value = None
            threshold = None

        results[preference] = {
            "status": status,
            "observed_value": observed_value,
            "threshold": threshold,
        }

    return {
        "environmental_preferences": results,
        "visual_support": assess_visual_support(environment),
        "comprehension": "not_assessed",
    }
