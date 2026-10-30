import unittest
from pathlib import Path

from src.agents.agent import (
    Agent,
    AgentProfile,
    AgentState,
    AgentCommunicationProfile,
)
from src.communication.vocabulary import CommunicationVocabulary


PROJECT_ROOT = Path(__file__).resolve().parents[1]

VOCABULARY_PATH = (
    PROJECT_ROOT / "config" / "communication_vocabulary.json"
)


class TestAgent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.vocabulary = CommunicationVocabulary.from_file(
            VOCABULARY_PATH
        )

    def test_create_agent(self):
        profile = AgentProfile(
            age_group="working_age_adult",
            hearing_profile="moderate",
            geography="regional",
            role="community_member",
            communication_profile=AgentCommunicationProfile(
                spoken_preferences=["face_to_face"],
                environmental_preferences=["quiet_environment"],
            ),
        )

        agent = Agent(
            agent_id="PERSON-001",
            profile=profile
        )

        agent.validate(self.vocabulary)

        self.assertEqual(agent.agent_id, "PERSON-001")
        self.assertEqual(agent.profile.hearing_profile, "moderate")
        self.assertEqual(agent.state.social_participation, 0.5)

    def test_empty_communication_profile_is_valid(self):
        profile = AgentCommunicationProfile()

        self.assertTrue(profile.validate(self.vocabulary))

    def test_valid_vocabulary_identifiers_are_accepted(self):
        profile = AgentCommunicationProfile(
            modalities=["spoken_communication"],
            spoken_preferences=["face_to_face"],
            environmental_preferences=["quiet_environment"],
        )

        self.assertTrue(profile.validate(self.vocabulary))

    def test_identifier_from_wrong_domain_is_rejected(self):
        profile = AgentCommunicationProfile(
            modalities=["quiet_environment"]
        )

        with self.assertRaises(ValueError):
            profile.validate(self.vocabulary)

    def test_unknown_identifier_is_rejected(self):
        profile = AgentCommunicationProfile(
            modalities=["unknown_communication_method"]
        )

        with self.assertRaises(ValueError):
            profile.validate(self.vocabulary)

    def test_duplicate_identifier_is_rejected(self):
        profile = AgentCommunicationProfile(
            modalities=[
                "spoken_communication",
                "spoken_communication",
            ]
        )

        with self.assertRaises(ValueError):
            profile.validate(self.vocabulary)

    def test_invalid_state_is_rejected(self):
        state = AgentState(social_participation=1.5)

        with self.assertRaises(ValueError):
            state.validate()

    def test_agent_summary(self):
        agent = Agent(
            agent_id="PERSON-002",
            profile=AgentProfile(
                age_group="older_adult",
                hearing_profile="severe",
                geography="remote_very_remote",
                communication_profile=AgentCommunicationProfile(
                    modalities=["spoken_communication"],
                ),
            )
        )

        summary = agent.summary()

        self.assertEqual(summary["agent_id"], "PERSON-002")
        self.assertEqual(summary["geography"], "remote_very_remote")
        self.assertEqual(
            summary["communication_profile"]["modalities"],
            ["spoken_communication"],
        )


if __name__ == "__main__":
    unittest.main()
