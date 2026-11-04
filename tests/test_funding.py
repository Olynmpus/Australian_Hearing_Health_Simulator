import pytest

from src.hearing_support.funding import FundingArrangement


def test_valid_public_funding_arrangement():
    arrangement = FundingArrangement(
        agent_id="PERSON-001",
        funding_pathway="public",
        eligibility_status="eligible",
        subsidy_amount=1000.0,
        out_of_pocket_cost=200.0,
        policy_reference="HSP",
        policy_version="2026",
        evidence_status="policy_supported",
    )

    assert arrangement.validate() is True


def test_valid_private_funding_arrangement():
    arrangement = FundingArrangement(
        agent_id="PERSON-002",
        funding_pathway="private",
        eligibility_status="unknown",
        private_contribution=500.0,
        out_of_pocket_cost=1500.0,
        evidence_status="user_reported",
    )

    assert arrangement.validate() is True


def test_default_values_represent_unknown_funding():
    arrangement = FundingArrangement(agent_id="PERSON-003")

    assert arrangement.validate() is True
    assert arrangement.funding_pathway == "unknown"
    assert arrangement.eligibility_status == "unknown"
    assert arrangement.subsidy_amount == 0.0


def test_invalid_agent_id_is_rejected():
    arrangement = FundingArrangement(agent_id=" ")

    with pytest.raises(ValueError, match="agent_id"):
        arrangement.validate()


def test_invalid_funding_pathway_is_rejected():
    arrangement = FundingArrangement(
        agent_id="PERSON-004",
        funding_pathway="automatic_eligibility",
    )

    with pytest.raises(ValueError, match="funding pathway"):
        arrangement.validate()


def test_invalid_eligibility_status_is_rejected():
    arrangement = FundingArrangement(
        agent_id="PERSON-005",
        eligibility_status="approved",
    )

    with pytest.raises(ValueError, match="eligibility status"):
        arrangement.validate()


@pytest.mark.parametrize(
    "amount",
    [-1.0, float("nan"), float("inf"), True, "500"],
)
def test_invalid_monetary_amount_is_rejected(amount):
    arrangement = FundingArrangement(
        agent_id="PERSON-006",
        subsidy_amount=amount,
    )

    with pytest.raises(ValueError, match="subsidy_amount"):
        arrangement.validate()


def test_invalid_evidence_status_is_rejected():
    arrangement = FundingArrangement(
        agent_id="PERSON-007",
        evidence_status="verified_by_ai",
    )

    with pytest.raises(ValueError, match="evidence status"):
        arrangement.validate()


def test_to_dict_returns_funding_information():
    arrangement = FundingArrangement(
        agent_id="PERSON-008",
        funding_pathway="mixed",
        eligibility_status="eligible",
        subsidy_amount=800.0,
        private_contribution=300.0,
        out_of_pocket_cost=400.0,
    )

    result = arrangement.to_dict()

    assert result["agent_id"] == "PERSON-008"
    assert result["funding_pathway"] == "mixed"
    assert result["subsidy_amount"] == 800.0
    assert result["private_contribution"] == 300.0
    assert result["out_of_pocket_cost"] == 400.0


def test_funding_pathway_valid_for_country():
    arrangement = FundingArrangement(
        agent_id="PERSON-009",
        funding_pathway="public",
    )

    country_profile = {
        "healthcare_system": {
            "funding_pathways": ["public", "private", "unknown"],
        }
    }

    assert arrangement.validate_country_pathways(country_profile) is True


def test_funding_pathway_not_supported_by_country_is_rejected():
    arrangement = FundingArrangement(
        agent_id="PERSON-010",
        funding_pathway="mixed",
    )

    country_profile = {
        "healthcare_system": {
            "funding_pathways": ["public", "private", "unknown"],
        }
    }

    with pytest.raises(ValueError, match="not supported"):
        arrangement.validate_country_pathways(country_profile)