import pytest

from src.service_capacity.age_suitability import AgeServiceSuitability


def make_suitability(**overrides):
    values = {
        "age_group": "older_adult",
        "service_type": "audiology_assessment",
        "suitability_status": "suitable",
        "requirements": [],
        "limitations": [],
        "evidence_status": "simulation_assumption",
    }

    values.update(overrides)
    return AgeServiceSuitability(**values)


def test_valid_age_service_suitability():
    assert make_suitability().validate() is True


def test_assessment_required_is_valid():
    assessment = make_suitability(
        suitability_status="assessment_required",
        requirements=["Individual clinical assessment"],
    )

    assert assessment.validate() is True


def test_unknown_suitability_is_valid():
    assessment = make_suitability(
        suitability_status="unknown",
    )

    assert assessment.validate() is True


def test_serialises_suitability():
    result = make_suitability(
        requirements=["Individual clinical assessment"],
        limitations=["Specialist equipment may be required"],
    ).to_dict()

    assert result["age_group"] == "older_adult"
    assert result["service_type"] == "audiology_assessment"
    assert result["requirements"] == [
        "Individual clinical assessment"
    ]
    assert result["limitations"] == [
        "Specialist equipment may be required"
    ]


@pytest.mark.parametrize(
    "field,value",
    [
        ("age_group", "unknown_age"),
        ("service_type", "invalid_service"),
        ("suitability_status", "probably_suitable"),
        ("requirements", "Individual assessment"),
        ("requirements", [""]),
        ("requirements", [None]),
        ("limitations", "Equipment required"),
        ("limitations", [""]),
        ("limitations", [None]),
        ("evidence_status", "unverified"),
    ],
)
def test_invalid_suitability_is_rejected(field, value):
    assessment = make_suitability(**{field: value})

    with pytest.raises(ValueError):
        assessment.validate()


@pytest.mark.parametrize(
    "age_group",
    [
        "infant",
        "preschool",
        "school_age",
        "adolescent",
        "working_age_adult",
        "older_adult",
    ],
)
def test_all_existing_age_groups_are_supported(age_group):
    assessment = make_suitability(age_group=age_group)

    assert assessment.validate() is True


def test_age_group_does_not_automatically_determine_suitability():
    infant = make_suitability(
        age_group="infant",
        suitability_status="unknown",
    )

    older_adult = make_suitability(
        age_group="older_adult",
        suitability_status="unknown",
    )

    assert infant.validate() is True
    assert older_adult.validate() is True
    assert infant.suitability_status == older_adult.suitability_status
