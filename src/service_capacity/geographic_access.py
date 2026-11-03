"""Geographic travel constraints for mobile hearing services."""

from dataclasses import dataclass
import math

from .funding import GEOGRAPHIES, EVIDENCE_STATUSES


@dataclass
class GeographicRoute:
    """Represents a planned mobile-service route to a destination.

    Distances and travel times must be explicitly supplied.
    This model does not infer travel from population geography categories.

    Calculated trips represent theoretical route capacity, not appointments
    or actual service attendance.
    """

    route_id: str
    service_id: str
    destination_geography: str
    round_trip_distance_km: float
    round_trip_travel_hours: float
    maximum_round_trip_distance_km: float
    available_travel_hours_per_month: float
    evidence_status: str

    def validate(self):
        for field_name in ("route_id", "service_id"):
            value = getattr(self, field_name)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

        if self.destination_geography not in GEOGRAPHIES:
            raise ValueError(
                f"Invalid destination geography: "
                f"{self.destination_geography}"
            )

        numeric_fields = (
            "round_trip_distance_km",
            "round_trip_travel_hours",
            "maximum_round_trip_distance_km",
            "available_travel_hours_per_month",
        )

        for field_name in numeric_fields:
            value = getattr(self, field_name)

            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value < 0
            ):
                raise ValueError(
                    f"{field_name} must be a finite, "
                    "non-negative number."
                )

        if self.round_trip_travel_hours <= 0:
            raise ValueError(
                "round_trip_travel_hours must be greater than zero."
            )

        if (
            not isinstance(self.evidence_status, str)
            or self.evidence_status not in EVIDENCE_STATUSES
        ):
            raise ValueError(
                f"Invalid evidence status: {self.evidence_status}"
            )

        return True

    def calculate_monthly_trip_capacity(self):
        """Calculate theoretical whole round trips per month."""

        self.validate()

        if (
            self.round_trip_distance_km
            > self.maximum_round_trip_distance_km
        ):
            return 0

        return math.floor(
            self.available_travel_hours_per_month
            / self.round_trip_travel_hours
        )

    def to_dict(self):
        self.validate()

        return {
            "route_id": self.route_id,
            "service_id": self.service_id,
            "destination_geography": self.destination_geography,
            "round_trip_distance_km": self.round_trip_distance_km,
            "round_trip_travel_hours": self.round_trip_travel_hours,
            "maximum_round_trip_distance_km": (
                self.maximum_round_trip_distance_km
            ),
            "available_travel_hours_per_month": (
                self.available_travel_hours_per_month
            ),
            "evidence_status": self.evidence_status,
        }
