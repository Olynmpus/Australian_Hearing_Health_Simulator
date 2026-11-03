import pytest

from src.service_capacity.geographic_access import GeographicRoute


def make_route(**overrides):
    values = {
        "route_id": "ROUTE-001",
        "service_id": "MOBILE-001",
        "destination_geography": "regional",
        "round_trip_distance_km": 300,
        "round_trip_travel_hours": 5,
        "maximum_round_trip_distance_km": 500,
        "available_travel_hours_per_month": 40,
        "evidence_status": "simulation_assumption",
    }

    values.update(overrides)
    return GeographicRoute(**values)


def test_valid_geographic_route():
    assert make_route().validate() is True


def test_calculates_monthly_trip_capacity():
    route = make_route(
        available_travel_hours_per_month=40,
        round_trip_travel_hours=5,
    )

    assert route.calculate_monthly_trip_capacity() == 8


def test_capacity_uses_whole_trips():
    route = make_route(
        available_travel_hours_per_month=10,
        round_trip_travel_hours=3,
    )

    assert route.calculate_monthly_trip_capacity() == 3


def test_route_beyond_maximum_distance_has_zero_capacity():
    route = make_route(
        round_trip_distance_km=600,
        maximum_round_trip_distance_km=500,
    )

    assert route.calculate_monthly_trip_capacity() == 0


def test_route_at_maximum_distance_is_allowed():
    route = make_route(
        round_trip_distance_km=500,
        maximum_round_trip_distance_km=500,
    )

    assert route.calculate_monthly_trip_capacity() == 8


def test_zero_available_travel_hours_produces_zero_capacity():
    route = make_route(available_travel_hours_per_month=0)

    assert route.calculate_monthly_trip_capacity() == 0


def test_serialises_geographic_route():
    result = make_route().to_dict()

    assert result["route_id"] == "ROUTE-001"
    assert result["destination_geography"] == "regional"
    assert result["round_trip_distance_km"] == 300


@pytest.mark.parametrize(
    "field,value",
    [
        ("route_id", ""),
        ("service_id", ""),
        ("destination_geography", "unknown"),
        ("round_trip_distance_km", -1),
        ("round_trip_distance_km", float("nan")),
        ("round_trip_distance_km", float("inf")),
        ("round_trip_distance_km", True),
        ("round_trip_travel_hours", 0),
        ("round_trip_travel_hours", -1),
        ("round_trip_travel_hours", float("inf")),
        ("maximum_round_trip_distance_km", -1),
        ("available_travel_hours_per_month", -1),
        ("available_travel_hours_per_month", float("nan")),
        ("available_travel_hours_per_month", True),
        ("evidence_status", "unverified"),
    ],
)
def test_invalid_geographic_route_is_rejected(field, value):
    route = make_route(**{field: value})

    with pytest.raises(ValueError):
        route.validate()


def test_travel_capacity_is_not_inferred_from_geography():
    route = make_route(
        destination_geography="remote_very_remote",
        round_trip_distance_km=300,
    )

    assert route.calculate_monthly_trip_capacity() == 8
