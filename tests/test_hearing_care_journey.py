import pytest

from src.hearing_support.journey import (
    HearingCareJourney,
    JourneyEvent,
)


def test_create_empty_journey():
    journey = HearingCareJourney(
        agent_id="PERSON-001",
        journey_id="JOURNEY-001",
    )

    assert journey.validate() is True
    assert journey.status == "not_started"
    assert journey.events == []


def test_add_journey_event():
    journey = HearingCareJourney(
        agent_id="PERSON-001",
        journey_id="JOURNEY-001",
    )

    event = JourneyEvent(
        month=1,
        event_type="help_sought",
        description="Person contacted a hearing service.",
        evidence_status="user_reported",
    )

    journey.add_event(event)

    assert len(journey.events) == 1
    assert journey.events[0].event_type == "help_sought"


def test_events_remain_in_recorded_order():
    journey = HearingCareJourney(
        agent_id="PERSON-001",
        journey_id="JOURNEY-001",
    )

    journey.add_event(
        JourneyEvent(1, "help_sought", "Contacted a service.")
    )
    journey.add_event(
        JourneyEvent(2, "service_unavailable", "No appointment available.")
    )

    result = journey.to_dict()

    assert result["events"][0]["event_type"] == "help_sought"
    assert result["events"][1]["event_type"] == "service_unavailable"


def test_adding_event_does_not_automatically_change_status():
    journey = HearingCareJourney(
        agent_id="PERSON-001",
        journey_id="JOURNEY-001",
    )

    journey.add_event(
        JourneyEvent(1, "help_sought", "Contacted a service.")
    )

    assert journey.status == "not_started"


def test_journey_status_can_be_updated_explicitly():
    journey = HearingCareJourney(
        agent_id="PERSON-001",
        journey_id="JOURNEY-001",
    )

    journey.set_status("active")

    assert journey.status == "active"


def test_invalid_journey_status_is_rejected():
    journey = HearingCareJourney(
        agent_id="PERSON-001",
        journey_id="JOURNEY-001",
    )

    with pytest.raises(ValueError, match="journey status"):
        journey.set_status("successful")


def test_invalid_event_month_is_rejected():
    event = JourneyEvent(
        month=-1,
        event_type="help_sought",
        description="Contacted a service.",
    )

    with pytest.raises(ValueError, match="month"):
        event.validate()


def test_invalid_event_description_is_rejected():
    event = JourneyEvent(
        month=1,
        event_type="help_sought",
        description=" ",
    )

    with pytest.raises(ValueError, match="description"):
        event.validate()


def test_invalid_event_evidence_status_is_rejected():
    event = JourneyEvent(
        month=1,
        event_type="help_sought",
        description="Contacted a service.",
        evidence_status="verified_by_ai",
    )

    with pytest.raises(ValueError, match="evidence status"):
        event.validate()


def test_invalid_agent_id_is_rejected():
    journey = HearingCareJourney(
        agent_id=" ",
        journey_id="JOURNEY-001",
    )

    with pytest.raises(ValueError, match="agent_id"):
        journey.validate()


def test_invalid_event_type_is_rejected():
    journey = HearingCareJourney(
        agent_id="PERSON-001",
        journey_id="JOURNEY-001",
    )

    with pytest.raises(ValueError, match="JourneyEvent"):
        journey.add_event("help_sought")


def test_journey_serialises_to_dictionary():
    journey = HearingCareJourney(
        agent_id="PERSON-001",
        journey_id="JOURNEY-001",
        status="active",
    )

    journey.add_event(
        JourneyEvent(
            month=1,
            event_type="assessment_requested",
            description="Person requested a hearing assessment.",
            evidence_status="user_reported",
        )
    )

    result = journey.to_dict()

    assert result["agent_id"] == "PERSON-001"
    assert result["journey_id"] == "JOURNEY-001"
    assert result["status"] == "active"
    assert len(result["events"]) == 1
    assert result["events"][0]["month"] == 1
def test_serialised_events_are_chronological():
    journey = HearingCareJourney(
        agent_id="PERSON-001",
        journey_id="JOURNEY-001",
    )

    journey.add_event(
        JourneyEvent(3, "assessment_completed", "Assessment completed.")
    )
    journey.add_event(
        JourneyEvent(1, "help_sought", "Help was requested.")
    )
    journey.add_event(
        JourneyEvent(2, "appointment_booked", "Appointment booked.")
    )

    result = journey.to_dict()

    months = [
        event["month"]
        for event in result["events"]
    ]

    assert months == [1, 2, 3]