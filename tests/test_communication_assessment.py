
import unittest

from src.behaviour.communication_model import CommunicationEnvironment
from src.behaviour.communication_assessment import (
    assess_acoustic_conditions,
    assess_visual_support,
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

if __name__ == "__main__":
    unittest.main()
