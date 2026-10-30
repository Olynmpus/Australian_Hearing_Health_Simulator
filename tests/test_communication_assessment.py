
import unittest

from src.agents.agent import AgentCommunicationProfile
from src.behaviour.communication_model import CommunicationEnvironment
from src.communication.vocabulary import CommunicationVocabulary
from src.behaviour.communication_assessment import (
    assess_acoustic_conditions,
    assess_visual_support,
    assess_communication_compatibility,
)


class TestCommunicationAssessment(unittest.TestCase):

    def test_ideal_speech_conditions(self):
        environment = CommunicationEnvironment()

        result = assess_acoustic_conditions(environment, "speech")

        self.assertEqual(result, 1.0)

    def test_noise_reduces_acoustic_indicator(self):
        environment = CommunicationEnvironment(
            background_noise=0.5
        )

        result = assess_acoustic_conditions(environment, "speech")

        self.assertEqual(result, 0.5)

    def test_poor_clarity_reduces_indicator(self):
        environment = CommunicationEnvironment(
            message_clarity=0.5
        )

        result = assess_acoustic_conditions(environment, "speech")

        self.assertEqual(result, 0.5)

    def test_increased_distance_reduces_indicator(self):
        environment = CommunicationEnvironment(
            distance_metres=5
        )

        result = assess_acoustic_conditions(environment, "speech")

        self.assertAlmostEqual(result, 0.6)

    def test_noise_does_not_affect_text_channel(self):
        environment = CommunicationEnvironment(
            background_noise=1.0
        )

        result = assess_acoustic_conditions(environment, "text")

        self.assertIsNone(result)

    def test_indicator_remains_bounded(self):
        environment = CommunicationEnvironment(
            background_noise=0.8,
            distance_metres=8,
            message_clarity=0.4,
        )

        result = assess_acoustic_conditions(environment, "speech")

        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

    def test_visual_support_available(self):
        environment = CommunicationEnvironment(
            speaker_face_visible=True,
            written_information_available=True,
        )

        result = assess_visual_support(environment)

        self.assertTrue(result["face_visible"])
        self.assertTrue(
            result["written_information_available"]
        )

    def test_visual_support_unavailable(self):
        environment = CommunicationEnvironment(
            speaker_face_visible=False,
            written_information_available=False,
        )

        result = assess_visual_support(environment)

        self.assertFalse(result["face_visible"])
        self.assertFalse(
            result["written_information_available"]
        )

    def test_visual_support_is_not_a_comprehension_score(self):
        environment = CommunicationEnvironment()

        result = assess_visual_support(environment)

        self.assertNotIn("comprehension", result)
        self.assertNotIn("understanding", result)

    # Communication compatibility tests

    def test_quiet_environment_preference_is_met(self):
        profile = AgentCommunicationProfile(
            environmental_preferences=["quiet_environment"]
        )
        environment = CommunicationEnvironment(
            background_noise=0.1
        )

        result = assess_communication_compatibility(
            profile, environment
        )

        self.assertEqual(
            result["environmental_preferences"]
            ["quiet_environment"]["status"],
            "met",
        )

    def test_quiet_environment_preference_is_not_met(self):
        profile = AgentCommunicationProfile(
            environmental_preferences=["quiet_environment"]
        )
        environment = CommunicationEnvironment(
            background_noise=0.7
        )

        result = assess_communication_compatibility(
            profile, environment
        )

        self.assertEqual(
            result["environmental_preferences"]
            ["quiet_environment"]["status"],
            "not_met",
        )

    def test_close_distance_preference_is_met(self):
        profile = AgentCommunicationProfile(
            environmental_preferences=["close_speaker_distance"]
        )
        environment = CommunicationEnvironment(
            distance_metres=1.5
        )

        result = assess_communication_compatibility(
            profile, environment
        )

        self.assertEqual(
            result["environmental_preferences"]
            ["close_speaker_distance"]["status"],
            "met",
        )

    def test_close_distance_preference_is_not_met(self):
        profile = AgentCommunicationProfile(
            environmental_preferences=["close_speaker_distance"]
        )
        environment = CommunicationEnvironment(
            distance_metres=4.0
        )

        result = assess_communication_compatibility(
            profile, environment
        )

        self.assertEqual(
            result["environmental_preferences"]
            ["close_speaker_distance"]["status"],
            "not_met",
        )

    def test_unsupported_preference_is_not_assessed(self):
        profile = AgentCommunicationProfile(
            environmental_preferences=["good_room_lighting"]
        )
        environment = CommunicationEnvironment()

        result = assess_communication_compatibility(
            profile, environment
        )

        self.assertEqual(
            result["environmental_preferences"]
            ["good_room_lighting"]["status"],
            "not_assessed",
        )

    def test_noise_preference_is_not_applicable_to_text(self):
        profile = AgentCommunicationProfile(
            environmental_preferences=["quiet_environment"]
        )
        environment = CommunicationEnvironment(
            background_noise=0.8
        )

        result = assess_communication_compatibility(
            profile, environment, channel="text"
        )

        self.assertEqual(
            result["environmental_preferences"]
            ["quiet_environment"]["status"],
            "not_applicable",
        )

    def test_visual_support_and_comprehension_are_separate(self):
        profile = AgentCommunicationProfile(
            environmental_preferences=["quiet_environment"]
        )
        environment = CommunicationEnvironment(
            speaker_face_visible=True,
            written_information_available=False,
        )

        result = assess_communication_compatibility(
            profile, environment
        )

        self.assertTrue(result["visual_support"]["face_visible"])
        self.assertFalse(
            result["visual_support"]["written_information_available"]
        )
        self.assertEqual(result["comprehension"], "not_assessed")

    def test_compatibility_rejects_identifier_from_wrong_domain(self):
        vocabulary = CommunicationVocabulary.from_file(
            "config/communication_vocabulary.json"
        )

        profile = AgentCommunicationProfile(
            environmental_preferences=["spoken_communication"]
        )

        environment = CommunicationEnvironment()

        with self.assertRaises(ValueError):
            assess_communication_compatibility(
                profile,
                environment,
                vocabulary=vocabulary,
            )

if __name__ == "__main__":
    unittest.main()
