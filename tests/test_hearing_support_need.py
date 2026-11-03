import unittest

from src.hearing_support.need import HearingSupportNeed


class TestHearingSupportNeed(unittest.TestCase):

    def make_record(self, **kwargs):
        values = {
            "agent_id": "PERSON-001",
            "assessment_month": 0,
        }
        values.update(kwargs)
        return HearingSupportNeed(**values)

    def test_default_record_is_valid(self):
        record = self.make_record()
        self.assertTrue(record.validate())

    def test_reported_difficulty_is_valid(self):
        record = self.make_record(
            functional_difficulty_status="difficulty_reported"
        )
        self.assertTrue(record.validate())

    def test_confirmed_functional_difficulty_is_valid(self):
        record = self.make_record(
            functional_difficulty_status="functional_difficulty_confirmed"
        )
        self.assertTrue(record.validate())

    def test_perceived_need_is_independent(self):
        record = self.make_record(
            functional_difficulty_status="unknown",
            perceived_need="yes",
        )
        self.assertTrue(record.validate())

    def test_help_seeking_intention_is_independent(self):
        record = self.make_record(
            perceived_need="yes",
            help_seeking_intention="no",
        )
        self.assertTrue(record.validate())

    def test_help_seeking_action_is_recorded(self):
        record = self.make_record(
            help_seeking_action="service_contacted"
        )
        self.assertTrue(record.validate())

    def test_evidence_status_is_recorded(self):
        record = self.make_record(
            evidence_status="user_reported"
        )
        self.assertTrue(record.validate())

    def test_negative_assessment_month_is_rejected(self):
        record = self.make_record(assessment_month=-1)
        with self.assertRaises(ValueError):
            record.validate()

    def test_boolean_assessment_month_is_rejected(self):
        record = self.make_record(assessment_month=True)
        with self.assertRaises(ValueError):
            record.validate()

    def test_invalid_functional_status_is_rejected(self):
        record = self.make_record(
            functional_difficulty_status="hearing_loss"
        )
        with self.assertRaises(ValueError):
            record.validate()

    def test_invalid_perceived_need_is_rejected(self):
        record = self.make_record(perceived_need="maybe")
        with self.assertRaises(ValueError):
            record.validate()

    def test_invalid_help_seeking_intention_is_rejected(self):
        record = self.make_record(help_seeking_intention="sometimes")
        with self.assertRaises(ValueError):
            record.validate()

    def test_invalid_help_seeking_action_is_rejected(self):
        record = self.make_record(help_seeking_action="bought_hearing_aid")
        with self.assertRaises(ValueError):
            record.validate()

    def test_invalid_evidence_status_is_rejected(self):
        record = self.make_record(evidence_status="verified")
        with self.assertRaises(ValueError):
            record.validate()

    def test_empty_agent_id_is_rejected(self):
        record = self.make_record(agent_id=" ")
        with self.assertRaises(ValueError):
            record.validate()

    def test_serialisation(self):
        record = self.make_record(
            assessment_month=3,
            functional_difficulty_status="difficulty_reported",
            perceived_need="yes",
            help_seeking_intention="yes",
            help_seeking_action="information_sought",
            evidence_status="user_reported",
        )

        result = record.to_dict()

        self.assertEqual(result["agent_id"], "PERSON-001")
        self.assertEqual(result["assessment_month"], 3)
        self.assertEqual(result["perceived_need"], "yes")
        self.assertEqual(result["help_seeking_action"], "information_sought")
        self.assertEqual(result["evidence_status"], "user_reported")


if __name__ == "__main__":
    unittest.main()
