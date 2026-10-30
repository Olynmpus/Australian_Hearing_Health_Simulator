import unittest

from src.agents.relationships import SocialRelationship
from src.behaviour.relationship_model import apply_relationship_experience


class TestRelationships(unittest.TestCase):

    def setUp(self):
        self.relationship = SocialRelationship(
            agent_id="PERSON-001",
            contact_id="FAMILY-001",
            relationship_type="family",
        )

    def test_create_relationship(self):
        self.relationship.validate()

        self.assertEqual(self.relationship.trust, 0.5)
        self.assertEqual(self.relationship.status, "active")

    def test_negative_interaction_changes_relationship(self):
        apply_relationship_experience(
            self.relationship,
            "negative_communication"
        )

        self.assertAlmostEqual(self.relationship.trust, 0.45)
        self.assertAlmostEqual(
            self.relationship.perceived_support, 0.45
        )

    def test_supportive_interaction_improves_relationship(self):
        apply_relationship_experience(
            self.relationship,
            "supportive_communication"
        )

        self.assertAlmostEqual(self.relationship.trust, 0.55)
        self.assertAlmostEqual(
            self.relationship.perceived_support, 0.60
        )

    def test_relationship_values_remain_bounded(self):
        self.relationship.trust = 0.98

        apply_relationship_experience(
            self.relationship,
            "supportive_communication"
        )

        self.assertEqual(self.relationship.trust, 1.0)

    def test_self_relationship_is_rejected(self):
        relationship = SocialRelationship(
            agent_id="PERSON-001",
            contact_id="PERSON-001",
            relationship_type="self",
        )

        with self.assertRaises(ValueError):
            relationship.validate()


if __name__ == "__main__":
    unittest.main()
