import pytest

from src.service_delivery.demand import ServiceDemand


def make_demand(**overrides):
    values = {
        "demand_id": "DEMAND-0001",
        "agent_id": "PERSON-000001",
        "service_type": "audiology_assessment",
        "request_month": 1,
        "request_source": "individual_request",
        "evidence_status": "simulation_assumption",
    }
    values.update(overrides)
    return ServiceDemand(**values)


def test_valid_service_demand():
    demand = make_demand()

    assert demand.validate() is True
    assert demand.to_dict()["demand_id"] == "DEMAND-0001"


@pytest.mark.parametrize("field", ["demand_id", "agent_id"])
def test_identifiers_must_not_be_empty(field):
    with pytest.raises(ValueError):
        make_demand(**{field: " "}).validate()


def test_invalid_service_type_is_rejected():
    with pytest.raises(ValueError):
        make_demand(service_type="invalid_service").validate()


@pytest.mark.parametrize("month", [-1, 1.5, True, "1"])
def test_invalid_request_month_is_rejected(month):
    with pytest.raises(ValueError):
        make_demand(request_month=month).validate()


def test_invalid_request_source_is_rejected():
    with pytest.raises(ValueError):
        make_demand(request_source="automatic").validate()


def test_invalid_evidence_status_is_rejected():
    with pytest.raises(ValueError):
        make_demand(evidence_status="unverified").validate()


def test_individual_can_have_multiple_service_demands():
    demands = [
        make_demand(
            demand_id="DEMAND-0001",
            service_type="audiology_assessment",
        ),
        make_demand(
            demand_id="DEMAND-0002",
            service_type="communication_support",
        ),
    ]

    assert all(demand.validate() for demand in demands)
    assert len({demand.demand_id for demand in demands}) == 2
    assert {demand.agent_id for demand in demands} == {"PERSON-000001"}
