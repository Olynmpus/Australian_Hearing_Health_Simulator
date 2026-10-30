import unittest

from src.agents.agent import AgentState
from src.behaviour.experience_model import apply_experience


class TestExperienceModel(unittest.TestCase):

    def test_negative_communication_changes_state(self):
        state = AgentState()

        changes = apply_experience(
            state,
            "negative_communication"
        )

        self.assertAlmostEqual(
            state.communication_confidence, 0.45
        )
        self.assertAlmostEqual(
            state.social_participation, 0.47
        )
        self.assertAlmostEqual(
            state.frustration, 0.10
        )

        self.assertIn("communication_confidence", changes)

    def test_supportive_experience_can_improve_state(self):
        state = AgentState()

        apply_experience(state, "supportive_communication")

        self.assertAlmostEqual(
            state.communication_confidence, 0.55
        )
        self.assertAlmostEqual(
            state.social_participation, 0.55
        )
        self.assertAlmostEqual(
            state.perceived_support, 0.55
        )

    def test_state_never_exceeds_bounds(self):
        state = AgentState(
            communication_confidence=0.98,
            frustration=0.95
        )

        apply_experience(state, "supportive_communication")

        self.assertEqual(state.communication_confidence, 1.0)
        self.assertAlmostEqual(state.frustration, 0.90)

    def test_unknown_outcome_is_rejected(self):
        state = AgentState()

        with self.assertRaises(ValueError):
            apply_experience(state, "unknown_experience")


if __name__ == "__main__":
    unittest.main()
