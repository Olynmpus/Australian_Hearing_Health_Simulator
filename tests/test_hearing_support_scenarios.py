"""Tests for the illustrative hearing-support scenarios."""

from src.simulation.hearing_support_scenarios import build_scenarios


def test_three_scenarios_are_created():
    records, definitions = build_scenarios()

    assert len(records) == 3
    assert len(definitions) == 3


def test_each_person_has_three_assessments():
    records, _ = build_scenarios()

    for record in records:
        assert len(record.hearing_support_needs) == 3
        assert [
            item.assessment_month
            for item in record.hearing_support_needs
        ] == [1, 3, 6]


def test_all_people_start_with_reported_difficulty():
    records, _ = build_scenarios()

    for record in records:
        first = record.hearing_support_needs[0]

        assert first.functional_difficulty_status == "difficulty_reported"
        assert first.perceived_need == "unknown"
        assert first.help_seeking_intention == "unknown"


def test_person_a_contacts_available_service():
    records, _ = build_scenarios()
    person = next(r for r in records if r.agent_id == "SCENARIO-A")

    final_need = person.hearing_support_needs[-1]
    service = person.service_access_records[0]

    assert final_need.perceived_need == "yes"
    assert final_need.help_seeking_intention == "yes"
    assert final_need.help_seeking_action == "service_contacted"

    assert service.availability_status == "available"
    assert service.appointment_status == "requested"


def test_person_b_does_not_seek_support():
    records, _ = build_scenarios()
    person = next(r for r in records if r.agent_id == "SCENARIO-B")

    final_need = person.hearing_support_needs[-1]

    assert final_need.functional_difficulty_status == "difficulty_reported"
    assert final_need.perceived_need == "no"
    assert final_need.help_seeking_intention == "no"
    assert final_need.help_seeking_action == "no_action"

    assert person.service_access_records == []


def test_person_c_contacts_unavailable_service():
    records, _ = build_scenarios()
    person = next(r for r in records if r.agent_id == "SCENARIO-C")

    final_need = person.hearing_support_needs[-1]
    service = person.service_access_records[0]

    assert final_need.perceived_need == "yes"
    assert final_need.help_seeking_intention == "yes"
    assert final_need.help_seeking_action == "service_contacted"

    assert service.availability_status == "unavailable"
    assert service.appointment_status == "not_available"


def test_people_a_and_c_have_different_access_outcomes():
    records, _ = build_scenarios()

    person_a = next(r for r in records if r.agent_id == "SCENARIO-A")
    person_c = next(r for r in records if r.agent_id == "SCENARIO-C")

    assert (
        person_a.hearing_support_needs[-1].help_seeking_action
        == person_c.hearing_support_needs[-1].help_seeking_action
    )

    assert (
        person_a.service_access_records[0].availability_status
        != person_c.service_access_records[0].availability_status
    )


def test_all_scenario_records_validate():
    records, _ = build_scenarios()

    for record in records:
        assert record.validate() is True

def test_all_scenario_assessments_are_labelled_as_assumptions():
    records, _ = build_scenarios()

    for record in records:
        for need in record.hearing_support_needs:
            assert need.evidence_status == "simulation_assumption"

        for service in record.service_access_records:
            assert service.evidence_status == "simulation_assumption"