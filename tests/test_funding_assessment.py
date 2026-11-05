import pytest

from src.service_capacity.costs import OperationalCost
from src.service_capacity.cost_assessment import assess_operational_costs
from src.service_capacity.assessment import assess_mobile_service_capacity
from src.service_capacity.age_suitability import AgeServiceSuitability
from src.service_capacity.deployment import MobileServiceDeployment
from src.service_capacity.geographic_access import GeographicRoute
from src.service_capacity.planned_schedule import create_planned_service_schedule
from src.service_capacity.workforce import WorkforceMember
from src.service_capacity.funding import OperationalFunding
from src.service_capacity.funding_assessment import assess_operational_funding


def make_cost_assessment(unknown=False):
    values = {
        "clinician_labour_per_hour": 50.0,
        "travel_per_trip": 200.0,
        "equipment_per_appointment": 10.0,
        "consumables_per_appointment": 5.0,
        "other_per_trip": 25.0,
        "other_per_appointment": 2.0,
    }

    costs = []

    for index, (component, amount) in enumerate(values.items(), start=1):
        is_unknown = unknown and component == "travel_per_trip"

        costs.append(
            OperationalCost(
                cost_id=f"COST-{index:03d}",
                cost_component=component,
                service_type="audiology_assessment",
                amount_aud=None if is_unknown else amount,
                evidence_status="unknown" if is_unknown else "simulation_assumption",
                description=f"Illustrative {component} cost",
            )
        )

    workforce = WorkforceMember(
        clinician_id="CLINICIAN-001",
        role="audiologist",
        qualifications=["Audiology qualification"],
        service_types=["audiology_assessment"],
        supported_age_groups=["working_age_adult"],
        available_clinical_hours_per_month=24,
        appointment_duration_minutes=60,
        evidence_status="simulation_assumption",
    )

    route = GeographicRoute(
        route_id="ROUTE-001",
        service_id="SERVICE-001",
        destination_geography="regional",
        round_trip_distance_km=200,
        round_trip_travel_hours=4,
        maximum_round_trip_distance_km=300,
        available_travel_hours_per_month=16,
        evidence_status="simulation_assumption",
    )

    deployment = MobileServiceDeployment(
        deployment_id="DEPLOYMENT-001",
        service_id="SERVICE-001",
        route_id="ROUTE-001",
        service_types=["audiology_assessment"],
        target_age_groups=["working_age_adult"],
        service_delivery_hours_per_trip=6,
        evidence_status="simulation_assumption",
    )

    suitability = AgeServiceSuitability(
        age_group="working_age_adult",
        service_type="audiology_assessment",
        suitability_status="suitable",
        requirements=[],
        limitations=[],
        evidence_status="simulation_assumption",
    )

    capacity = assess_mobile_service_capacity(
        workforce,
        route,
        deployment,
        suitability,
        "audiology_assessment",
        "working_age_adult",
    )

    schedule = create_planned_service_schedule(
        capacity_assessment=capacity,
        workforce=workforce,
        deployment=deployment,
        planned_trips_per_month=4,
        planned_appointments_per_month=24,
        planned_clinical_hours_per_month=24,
    )

    return assess_operational_costs(
        costs=costs,
        service_type="audiology_assessment",
        planned_schedule=schedule,
    )


def make_funding(**overrides):
    values = {
        "funding_id": "FUND-001",
        "funding_source": "Government",
        "funding_program": "Regional Hearing Services",
        "available_amount_aud": 3000.0,
        "period_months": 12,
        "service_types": ["audiology_assessment"],
        "target_geographies": ["regional"],
        "evidence_status": "simulation_assumption",
    }

    values.update(overrides)
    return OperationalFunding(**values)


def assess(funding_records=None, cost_assessment=None, **overrides):
    arguments = {
        "funding_records": [make_funding()] if funding_records is None else funding_records,
        "cost_assessment": make_cost_assessment() if cost_assessment is None else cost_assessment,
        "service_type": "audiology_assessment",
        "geography": "regional",
        "operating_months": 12,
    }

    arguments.update(overrides)
    return assess_operational_funding(**arguments)


def test_sufficient_funding():
    result = assess(
        funding_records=[make_funding(available_amount_aud=31000)]
    )

    assert result.total_available_funding_aud == 31000
    assert result.monthly_operational_cost_aud == 2508
    assert result.estimated_operational_cost_aud == 30096
    assert result.funding_balance_aud == 904
    assert result.assessment_status == "sufficient"


def test_insufficient_funding():
    result = assess(
        funding_records=[
            make_funding(available_amount_aud=2000)
        ]
    )

    assert result.funding_balance_aud == -28096
    assert result.assessment_status == "insufficient"


def test_multiple_funding_sources_are_aggregated():
    funding = [
        make_funding(),
        make_funding(
            funding_id="FUND-002",
            funding_source="Organisation",
            available_amount_aud=1000,
        ),
    ]

    result = assess(funding_records=funding)

    assert result.total_available_funding_aud == 4000
    assert result.funding_balance_aud == -26096
    assert result.funding_ids == ["FUND-001", "FUND-002"]


def test_duplicate_funding_ids_are_rejected():
    with pytest.raises(ValueError, match="Duplicate funding IDs"):
        assess(funding_records=[make_funding(), make_funding()])


def test_non_matching_geography_is_excluded():
    result = assess(
        funding_records=[
            make_funding(target_geographies=["metropolitan"])
        ]
    )

    assert result.total_available_funding_aud is None
    assert result.assessment_status == "incomplete"
    assert "FUND-001" in result.reasons[0]


def test_non_matching_service_is_excluded():
    result = assess(
        funding_records=[
            make_funding(service_types=["rehabilitation"])
        ]
    )

    assert result.total_available_funding_aud is None
    assert result.assessment_status == "incomplete"


def test_period_mismatch_is_not_comparable():
    result = assess(
        funding_records=[
            make_funding(period_months=6)
        ]
    )

    assert result.assessment_status == "not_comparable"
    assert result.total_available_funding_aud is None
    assert result.funding_balance_aud is None


def test_unknown_cost_produces_incomplete_assessment():
    result = assess(cost_assessment=make_cost_assessment(unknown=True))

    assert result.assessment_status == "incomplete"
    assert result.total_available_funding_aud == 3000
    assert result.estimated_operational_cost_aud is None
    assert result.funding_balance_aud is None


def test_invalid_assessment_period_is_rejected():
    with pytest.raises(ValueError, match="operating_months"):
        assess(operating_months=0)


def test_mismatched_cost_service_is_rejected():
    cost = make_cost_assessment()
    cost.service_type = "rehabilitation"

    with pytest.raises(ValueError, match="service type does not match"):
        assess(cost_assessment=cost)


def test_serialises_funding_assessment():
    result = assess(
        funding_records=[make_funding(available_amount_aud=31000)]
    )
    data = result.to_dict()

    assert data["assessment_status"] == "sufficient"
    assert data["funding_evidence_statuses"]["FUND-001"] == "simulation_assumption"


def test_evidence_quality_is_simulation_assumption():
    result = assess()

    assert result.evidence_quality == "simulation_assumption"
    assert result.assessment_status == "insufficient"


def test_evidence_quality_is_policy_supported():
    cost = make_cost_assessment()
    cost.evidence_statuses = {
        component: "policy_supported"
        for component in cost.evidence_statuses
    }

    result = assess(
        funding_records=[
            make_funding(
                available_amount_aud=31000,
                evidence_status="policy_supported",
            )
        ],
        cost_assessment=cost,
    )

    assert result.evidence_quality == "policy_supported"
    assert result.assessment_status == "sufficient"


def test_evidence_quality_is_user_reported():
    cost = make_cost_assessment()
    cost.evidence_statuses = {
        component: "policy_supported"
        for component in cost.evidence_statuses
    }

    result = assess(
        funding_records=[
            make_funding(
                available_amount_aud=31000,
                evidence_status="user_reported",
            )
        ],
        cost_assessment=cost,
    )

    assert result.evidence_quality == "user_reported"
    assert result.assessment_status == "sufficient"


def test_evidence_quality_is_mixed_when_unknown_is_combined():
    result = assess(
        cost_assessment=make_cost_assessment(unknown=True)
    )

    assert result.evidence_quality == "mixed"
    assert result.assessment_status == "incomplete"


def test_evidence_quality_is_unknown_when_all_evidence_is_unknown():
    cost = make_cost_assessment(unknown=True)
    cost.evidence_statuses = {
        component: "unknown"
        for component in cost.evidence_statuses
    }

    result = assess(
        funding_records=[
            make_funding(evidence_status="unknown")
        ],
        cost_assessment=cost,
    )

    assert result.evidence_quality == "unknown"
    assert result.assessment_status == "incomplete"


def test_funding_and_cost_evidence_are_preserved_separately():
    cost = make_cost_assessment()
    cost.evidence_statuses["travel_per_trip"] = "policy_supported"

    funding = make_funding(evidence_status="user_reported")

    result = assess(
        funding_records=[funding],
        cost_assessment=cost,
    )

    assert result.funding_evidence_statuses == {
        "FUND-001": "user_reported"
    }
    assert result.cost_evidence_statuses == cost.evidence_statuses
    assert result.cost_evidence_statuses["travel_per_trip"] == (
        "policy_supported"
    )


def test_evidence_quality_does_not_change_funding_calculation():
    cost = make_cost_assessment()
    cost.evidence_statuses = {
        component: "policy_supported"
        for component in cost.evidence_statuses
    }

    policy_result = assess(
        funding_records=[
            make_funding(
                available_amount_aud=31000,
                evidence_status="policy_supported",
            )
        ],
        cost_assessment=cost,
    )

    assumption_result = assess(
        funding_records=[
            make_funding(
                available_amount_aud=31000,
                evidence_status="simulation_assumption",
            )
        ],
        cost_assessment=cost,
    )

    assert policy_result.evidence_quality == "policy_supported"
    assert assumption_result.evidence_quality == "simulation_assumption"

    assert (
        policy_result.total_available_funding_aud
        == assumption_result.total_available_funding_aud
    )
    assert (
        policy_result.estimated_operational_cost_aud
        == assumption_result.estimated_operational_cost_aud
    )
    assert (
        policy_result.funding_balance_aud
        == assumption_result.funding_balance_aud
    )
    assert (
        policy_result.assessment_status
        == assumption_result.assessment_status
    )

def test_child_allocation_is_not_double_counted():
    funding = [
        make_funding(
            funding_id="FUND-PARENT",
            available_amount_aud=10000,
        ),
        make_funding(
            funding_id="FUND-CHILD",
            parent_funding_id="FUND-PARENT",
            available_amount_aud=2000,
        ),
    ]

    result = assess(funding_records=funding)

    assert result.total_available_funding_aud == 10000
    assert result.funding_ids == ["FUND-PARENT"]
    assert any(
        "FUND-CHILD" in reason
        for reason in result.reasons
    )


def test_child_is_counted_when_parent_is_outside_scope():
    funding = [
        make_funding(
            funding_id="FUND-PARENT",
            target_geographies=["metropolitan"],
            available_amount_aud=10000,
        ),
        make_funding(
            funding_id="FUND-CHILD",
            parent_funding_id="FUND-PARENT",
            target_geographies=["regional"],
            available_amount_aud=2000,
        ),
    ]

    result = assess(funding_records=funding)

    assert result.total_available_funding_aud == 2000
    assert result.funding_ids == ["FUND-CHILD"]


def test_independent_allocations_are_both_counted():
    funding = [
        make_funding(
            funding_id="FUND-001",
            available_amount_aud=10000,
        ),
        make_funding(
            funding_id="FUND-002",
            available_amount_aud=2000,
        ),
    ]

    result = assess(funding_records=funding)

    assert result.total_available_funding_aud == 12000
    assert result.funding_ids == ["FUND-001", "FUND-002"]


def test_missing_parent_funding_record_is_rejected():
    funding = [
        make_funding(
            funding_id="FUND-CHILD",
            parent_funding_id="FUND-MISSING",
        )
    ]

    with pytest.raises(ValueError, match="does not exist"):
        assess(funding_records=funding)


def test_circular_funding_relationships_are_rejected():
    funding = [
        make_funding(
            funding_id="FUND-A",
            parent_funding_id="FUND-B",
        ),
        make_funding(
            funding_id="FUND-B",
            parent_funding_id="FUND-A",
        ),
    ]

    with pytest.raises(ValueError, match="Circular"):
        assess(funding_records=funding)


def test_nested_child_allocations_are_not_double_counted():
    funding = [
        make_funding(
            funding_id="FUND-A",
            available_amount_aud=10000,
        ),
        make_funding(
            funding_id="FUND-B",
            parent_funding_id="FUND-A",
            available_amount_aud=5000,
        ),
        make_funding(
            funding_id="FUND-C",
            parent_funding_id="FUND-B",
            available_amount_aud=2000,
        ),
    ]

    result = assess(funding_records=funding)

    assert result.total_available_funding_aud == 10000
    assert result.funding_ids == ["FUND-A"]

def test_nested_child_is_excluded_when_grandparent_matches_scope():
    funding = [
        make_funding(
            funding_id="FUND-A",
            available_amount_aud=10000,
        ),
        make_funding(
            funding_id="FUND-B",
            parent_funding_id="FUND-A",
            target_geographies=["metropolitan"],
            available_amount_aud=5000,
        ),
        make_funding(
            funding_id="FUND-C",
            parent_funding_id="FUND-B",
            target_geographies=["regional"],
            available_amount_aud=2000,
        ),
    ]

    result = assess(funding_records=funding)

    assert result.total_available_funding_aud == 10000
    assert result.funding_ids == ["FUND-A"]

def test_parent_funding_id_cannot_be_blank():
    with pytest.raises(ValueError, match="non-empty string"):
        make_funding(parent_funding_id="   ")


def test_parent_funding_id_cannot_be_blank():
    funding = make_funding(parent_funding_id="   ")

    with pytest.raises(ValueError, match="non-empty string"):
        assess(funding_records=[funding])


def test_funding_record_cannot_be_its_own_parent():
    funding = make_funding(
        funding_id="FUND-001",
        parent_funding_id="FUND-001",
    )

    with pytest.raises(ValueError, match="own parent"):
        assess(funding_records=[funding])