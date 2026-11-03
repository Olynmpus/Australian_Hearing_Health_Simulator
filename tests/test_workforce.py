import pytest

from src.service_capacity.workforce import WorkforceMember


def make_member(**overrides):
    values = {
        "clinician_id": "CLIN-001",
        "role": "audiologist",
        "qualifications": ["Audiology qualification"],
        "service_types": ["audiology_assessment"],
        "supported_age_groups": ["working_age_adult"],
        "available_clinical_hours_per_month": 40,
        "appointment_duration_minutes": 60,
        "evidence_status": "simulation_assumption",
    }

    values.update(overrides)
    return WorkforceMember(**values)


def test_valid_workforce_member():
    assert make_member().validate() is True


def test_calculates_monthly_appointment_capacity():
    member = make_member(
        available_clinical_hours_per_month=40,
        appointment_duration_minutes=60,
    )

    assert member.calculate_monthly_appointment_capacity(
        "audiology_assessment"
    ) == 40


def test_capacity_uses_whole_appointments():
    member = make_member(
        available_clinical_hours_per_month=10,
        appointment_duration_minutes=45,
    )

    assert member.calculate_monthly_appointment_capacity(
        "audiology_assessment"
    ) == 13


def test_service_outside_declared_scope_has_zero_capacity():
    member = make_member()

    assert member.calculate_monthly_appointment_capacity(
        "rehabilitation"
    ) == 0


def test_zero_available_hours_produces_zero_capacity():
    member = make_member(available_clinical_hours_per_month=0)

    assert member.calculate_monthly_appointment_capacity(
        "audiology_assessment"
    ) == 0


def test_serialises_workforce_member():
    result = make_member().to_dict()

    assert result["clinician_id"] == "CLIN-001"
    assert result["role"] == "audiologist"
    assert result["service_types"] == ["audiology_assessment"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("clinician_id", ""),
        ("role", "unqualified_role"),
        ("qualifications", []),
        ("qualifications", [""]),
        ("service_types", []),
        ("service_types", ["invalid_service"]),
        ("service_types", ["audiology_assessment"] * 2),
        ("available_clinical_hours_per_month", -1),
        ("available_clinical_hours_per_month", float("nan")),
        ("available_clinical_hours_per_month", float("inf")),
        ("available_clinical_hours_per_month", True),
        ("appointment_duration_minutes", 0),
        ("appointment_duration_minutes", -30),
        ("appointment_duration_minutes", 30.5),
        ("appointment_duration_minutes", True),
        ("evidence_status", "unverified"),
    ],
)
def test_invalid_workforce_member_is_rejected(field, value):
    member = make_member(**{field: value})

    with pytest.raises(ValueError):
        member.validate()


def test_invalid_service_type_query_is_rejected():
    member = make_member()

    with pytest.raises(ValueError):
        member.calculate_monthly_appointment_capacity("invalid")


def test_capacity_is_not_inferred_from_job_title():
    member = make_member(
        role="audiology_assistant",
        service_types=["communication_support"],
    )

    assert member.calculate_monthly_appointment_capacity(
        "audiology_assessment"
    ) == 0
