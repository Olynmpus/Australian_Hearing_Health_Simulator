"""Associates an individual with their hearing-support records."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.agents.agent import Agent
from src.hearing_support.funding import FundingArrangement
from src.hearing_support.service_access import ServiceAccess
from src.hearing_support.journey import HearingCareJourney
from src.hearing_support.need import HearingSupportNeed


@dataclass
class IndividualHearingSupportRecord:
    """Combined hearing-support record for one individual."""

    agent: Agent

    funding_arrangements: list[FundingArrangement] = field(
        default_factory=list
    )
    service_access_records: list[ServiceAccess] = field(
        default_factory=list
    )
    journeys: list[HearingCareJourney] = field(
        default_factory=list
    )
    hearing_support_needs: list[HearingSupportNeed] = field(
        default_factory=list
    )
    service_demands: list[ServiceDemand] = field(
        default_factory=list
    )
    service_allocations: list[ServiceAllocation] = field(
        default_factory=list
    )
    service_deliveries: list[ServiceDelivery] = field(
        default_factory=list
    )

    @property
    def agent_id(self):
        return self.agent.agent_id

    def _validate_association(self, record, expected_type, label):
        if not isinstance(record, expected_type):
            raise ValueError(
                f"{label} must be a {expected_type.__name__}."
            )

        record.validate()

        if record.agent_id != self.agent_id:
            raise ValueError(
                f"{label} agent_id does not match the individual."
            )

    def add_funding_arrangement(self, arrangement):
        self._validate_association(
            arrangement, FundingArrangement, "Funding arrangement"
        )
        self.funding_arrangements.append(arrangement)

    def add_service_access(self, service_access):
        self._validate_association(
            service_access, ServiceAccess, "Service access record"
        )
        self.service_access_records.append(service_access)

    def add_journey(self, journey):
        self._validate_association(
            journey, HearingCareJourney, "Hearing-care journey"
        )
        self.journeys.append(journey)

    def add_hearing_support_need(self, need):
        self._validate_association(
            need, HearingSupportNeed, "Hearing-support need"
        )
        self.hearing_support_needs.append(need)

    def add_service_demand(self, demand):
        from src.service_delivery.demand import ServiceDemand
        self._validate_association(
            demand, ServiceDemand, "Service demand"
        )
        self.service_demands.append(demand)

    def add_service_allocation(self, allocation):
        from src.service_delivery.allocation import ServiceAllocation
        self._validate_association(
            allocation, ServiceAllocation, "Service allocation"
        )
        self.service_allocations.append(allocation)

    def add_service_delivery(self, delivery):
        from src.service_delivery.delivery import ServiceDelivery
        self._validate_association(
            delivery, ServiceDelivery, "Service delivery"
        )
        self.service_deliveries.append(delivery)

    def validate(self):
        """Validate the individual and all associated records."""

        from src.service_delivery.demand import ServiceDemand
        from src.service_delivery.allocation import ServiceAllocation
        from src.service_delivery.delivery import ServiceDelivery

        if not isinstance(self.agent, Agent):
            raise ValueError("agent must be an Agent.")

        self.agent.validate()

        collections = (
            ("funding_arrangements", self.funding_arrangements),
            ("service_access_records", self.service_access_records),
            ("journeys", self.journeys),
            ("hearing_support_needs", self.hearing_support_needs),
            ("service_demands", self.service_demands),
            ("service_allocations", self.service_allocations),
            ("service_deliveries", self.service_deliveries),
        )

        for label, records in collections:
            if not isinstance(records, list):
                raise ValueError(f"{label} must be a list.")

        record_types = (
            (self.funding_arrangements, FundingArrangement,
             "Funding arrangement"),
            (self.service_access_records, ServiceAccess,
             "Service access record"),
            (self.journeys, HearingCareJourney,
             "Hearing-care journey"),
            (self.hearing_support_needs, HearingSupportNeed,
             "Hearing-support need"),
            (self.service_demands, ServiceDemand, "Service demand"),
            (self.service_allocations, ServiceAllocation,
             "Service allocation"),
            (self.service_deliveries, ServiceDelivery,
             "Service delivery"),
        )

        for records, expected_type, label in record_types:
            for record in records:
                self._validate_association(
                    record, expected_type, label
                )

        return True

    def to_dict(self):
        """Return the individual and associated records as dictionaries."""

        self.validate()

        return {
            "agent": self.agent.summary(),
            "funding_arrangements": [
                record.to_dict()
                for record in self.funding_arrangements
            ],
            "service_access_records": [
                record.to_dict()
                for record in self.service_access_records
            ],
            "journeys": [
                record.to_dict()
                for record in self.journeys
            ],
            "hearing_support_needs": [
                record.to_dict()
                for record in sorted(
                    self.hearing_support_needs,
                    key=lambda item: item.assessment_month,
                )
            ],
            "service_demands": [
                record.to_dict()
                for record in sorted(
                    self.service_demands,
                    key=lambda item: item.request_month,
                )
            ],
            "service_allocations": [
                record.to_dict()
                for record in self.service_allocations
            ],
            "service_deliveries": [
                record.to_dict()
                for record in sorted(
                    self.service_deliveries,
                    key=lambda item: item.delivery_month,
                )
            ],
        }
