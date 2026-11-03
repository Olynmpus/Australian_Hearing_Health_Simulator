import pytest

from src.hearing_support.service_access import ServiceAccess


def test_create_default_service_access():
    access = ServiceAccess(agent_id="PERSON-001")

    assert access.validate() is True
    assert access.service_type == "unknown"
    assert access.pathway == "unknown"
    assert access.availability_status == "unknown"
    assert access.appointment_status == "unknown"
    assert access.attendance_status == "unknown"
    assert access.waiting_time_days is None


def test_record_service_access():
    access = ServiceAccess(
        agent_id="PERSON-001",
        service_type="audiology_assessment",
        pathway="public",
        availability_status="available",
        appointment_status="scheduled",
        attendance_status="not_yet_due",
        waiting_time_days=30,
        evidence_status="user_reported",
    )

    assert access.validate() is True


def test_service_access_serialises_to_dictionary():
    access = ServiceAccess(
        agent_id="PERSON-001",
        service_type="audiology_assessment",
        pathway="public",
    )

    result = access.to_dict()

    assert result["agent_id"] == "PERSON-001"
    assert result["service_type"] == "audiology_assessment"
    assert result["waiting_time_days"] is None


def test_invalid_service_type_is_rejected():
    access = ServiceAccess(
        agent_id="PERSON-001",
        service_type="invalid_service",
    )

    with pytest.raises(ValueError):
        access.validate()


def test_invalid_pathway_is_rejected():
    access = ServiceAccess(
        agent_id="PERSON-001",
        pathway="invalid_pathway",
    )

    with pytest.raises(ValueError):
        access.validate()


def test_invalid_availability_status_is_rejected():
    access = ServiceAccess(
        agent_id="PERSON-001",
        availability_status="invalid",
    )

    with pytest.raises(ValueError):
        access.validate()


def test_invalid_appointment_status_is_rejected():
    access = ServiceAccess(
        agent_id="PERSON-001",
        appointment_status="invalid",
    )

    with pytest.raises(ValueError):
        access.validate()


def test_invalid_attendance_status_is_rejected():
    access = ServiceAccess(
        agent_id="PERSON-001",
        attendance_status="invalid",
    )

    with pytest.raises(ValueError):
        access.validate()


def test_negative_waiting_time_is_rejected():
    access = ServiceAccess(
        agent_id="PERSON-001",
        waiting_time_days=-1,
    )

    with pytest.raises(ValueError):
        access.validate()


def test_boolean_waiting_time_is_rejected():
    access = ServiceAccess(
        agent_id="PERSON-001",
        waiting_time_days=True,
    )

    with pytest.raises(ValueError):
        access.validate()


def test_blank_agent_id_is_rejected():
    access = ServiceAccess(agent_id=" ")

    with pytest.raises(ValueError):
        access.validate()