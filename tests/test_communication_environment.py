
import unittest

from src.behaviour.communication_model import CommunicationEnvironment


class TestCommunicationEnvironment(unittest.TestCase):

    def test_default_environment(self):
        environment = CommunicationEnvironment()
        self.assertTrue(environment.validate())

    def test_visual_access_can_be_unavailable(self):
        environment = CommunicationEnvironment(
            speaker_face_visible=False,
            written_information_available=False,
        )
        self.assertTrue(environment.validate())

    def test_written_information_can_be_available(self):
        environment = CommunicationEnvironment(
            written_information_available=True,
        )
        self.assertTrue(environment.validate())

    def test_invalid_background_noise_is_rejected(self):
        environment = CommunicationEnvironment(background_noise=1.5)

        with self.assertRaises(ValueError):
            environment.validate()

    def test_negative_distance_is_rejected(self):
        environment = CommunicationEnvironment(distance_metres=-1)

        with self.assertRaises(ValueError):
            environment.validate()

    def test_invalid_message_clarity_is_rejected(self):
        environment = CommunicationEnvironment(message_clarity=-0.1)

        with self.assertRaises(ValueError):
            environment.validate()


if __name__ == "__main__":
    unittest.main()
