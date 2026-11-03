import unittest

from src.agents.agent import Agent, AgentProfile
from src.hearing_support.individual_record import (
    IndividualHearingSupportRecord,
)
from src.hearing_support.need import HearingSupportNeed


class TestHearingSupportNeedIntegration(unittest.TestCase):

    def setUp(self):
        self.agent = Agent(
            agent_id="PERSON-001",
            profile=AgentProfile(
                age_group="working_age_adult",
                hearing_profile="normal",
                geography="metropolitan",
            ),
        )

        self.record = IndividualHearingSupportRecord(
            agent=self.agent
        )

    def make_need(self, month, **kwargs):
        return HearingSupportNeed(
            agent_id="PERSON-001",
            assessment_month=month,
            **kwargs,
        )

    def test_empty_need_history(self):
        self.assertEqual(self.record.hearing_support_needs, [])
        self.assertTrue(self.record.validate())

    def test_add_one_need_record(self):
        need = self.make_need(0)

        self.record.add_hearing_support_need(need)

        self.assertEqual(len(self.record.hearing_support_needs), 1)
        self.assertTrue(self.record.validate())

    def test_multiple_assessments_are_preserved(self):
        first = self.make_need(0, perceived_need="no")
        second = self.make_need(6, perceived_need="yes")

        self.record.add_hearing_support_need(first)
        self.record.add_hearing_support_need(second)

        self.assertEqual(len(self.record.hearing_support_needs), 2)

    def test_same_month_assessments_are_not_discarded(self):
        first = self.make_need(3, perceived_need="no")
        second = self.make_need(3, perceived_need="yes")

        self.record.add_hearing_support_need(first)
        self.record.add_hearing_support_need(second)

        self.assertEqual(len(self.record.hearing_support_needs), 2)

    def test_wrong_agent_id_is_rejected(self):
        need = HearingSupportNeed(
            agent_id="PERSON-999",
            assessment_month=0,
        )

        with self.assertRaises(ValueError):
            self.record.add_hearing_support_need(need)

    def test_wrong_record_type_is_rejected(self):
        with self.assertRaises(ValueError):
            self.record.add_hearing_support_need("not a need record")

    def test_serialisation_orders_assessments_by_month(self):
        self.record.add_hearing_support_need(
            self.make_need(6, perceived_need="yes")
        )
        self.record.add_hearing_support_need(
            self.make_need(0, perceived_need="no")
        )

        result = self.record.to_dict()

        months = [
            item["assessment_month"]
            for item in result["hearing_support_needs"]
        ]

        self.assertEqual(months, [0, 6])

    def test_serialisation_preserves_assessment_history(self):
        self.record.add_hearing_support_need(
            self.make_need(
                0,
                perceived_need="no",
                evidence_status="user_reported",
            )
        )
        self.record.add_hearing_support_need(
            self.make_need(
                6,
                perceived_need="yes",
                evidence_status="user_reported",
            )
        )

        result = self.record.to_dict()
        history = result["hearing_support_needs"]

        self.assertEqual(history[0]["perceived_need"], "no")
        self.assertEqual(history[1]["perceived_need"], "yes")

    def test_invalid_record_in_list_is_detected(self):
        self.record.hearing_support_needs.append("invalid")

        with self.assertRaises(ValueError):
            self.record.validate()


if __name__ == "__main__":
    unittest.main()
