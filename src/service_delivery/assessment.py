"""Integrated assessment of hearing-service demand, allocation and delivery."""

from dataclasses import asdict, dataclass

from .demand import ServiceDemand
from .allocation import ServiceAllocation
from .delivery import ServiceDelivery


@dataclass
class ServiceDeliveryAssessment:
    """Summary of the individual service delivery pathway."""

    requested_count: int
    allocated_count: int
    unallocated_count: int
    attendance_recorded_count: int
    attended_count: int
    did_not_attend_count: int
    delivery_recorded_count: int
    delivered_count: int
    not_delivered_count: int
    pending_delivery_count: int

    def to_dict(self):
        return asdict(self)


def assess_service_delivery(
    demands: list[ServiceDemand],
    allocations: list[ServiceAllocation],
    deliveries: list[ServiceDelivery],
) -> ServiceDeliveryAssessment:
    """Validate and summarise the service delivery pathway."""

    for name, records in (
        ("demands", demands),
        ("allocations", allocations),
        ("deliveries", deliveries),
    ):
        if not isinstance(records, list):
            raise TypeError(f"{name} must be a list.")

    demand_lookup = {}

    for demand in demands:
        if not isinstance(demand, ServiceDemand):
            raise TypeError("Every demand must be a ServiceDemand.")

        demand.validate()

        if demand.demand_id in demand_lookup:
            raise ValueError(f"Duplicate demand ID: {demand.demand_id}")

        demand_lookup[demand.demand_id] = demand

    allocation_lookup = {}

    for allocation in allocations:
        if not isinstance(allocation, ServiceAllocation):
            raise TypeError(
                "Every allocation must be a ServiceAllocation."
            )

        allocation.validate()

        if allocation.demand_id in allocation_lookup:
            raise ValueError(
                f"Duplicate allocation for demand: {allocation.demand_id}"
            )

        demand = demand_lookup.get(allocation.demand_id)

        if demand is None:
            raise ValueError(
                f"Allocation references unknown demand: "
                f"{allocation.demand_id}"
            )

        if (
            allocation.agent_id != demand.agent_id
            or allocation.service_type != demand.service_type
        ):
            raise ValueError(
                f"Allocation does not match demand: {allocation.demand_id}"
            )

        allocation_lookup[allocation.demand_id] = allocation

    missing_allocations = (
        set(demand_lookup) - set(allocation_lookup)
    )

    if missing_allocations:
        raise ValueError(
            "Every demand must have an allocation outcome. "
            f"Missing: {sorted(missing_allocations)}"
        )

    delivery_lookup = {}

    for delivery in deliveries:
        if not isinstance(delivery, ServiceDelivery):
            raise TypeError(
                "Every delivery must be a ServiceDelivery."
            )

        delivery.validate()

        if delivery.demand_id in delivery_lookup:
            raise ValueError(
                f"Duplicate delivery for demand: {delivery.demand_id}"
            )

        allocation = allocation_lookup.get(delivery.demand_id)

        if allocation is None:
            raise ValueError(
                f"Delivery references unknown demand: {delivery.demand_id}"
            )

        if allocation.allocation_status != "allocated":
            raise ValueError(
                f"Delivery references unallocated demand: "
                f"{delivery.demand_id}"
            )

        if (
            delivery.agent_id != allocation.agent_id
            or delivery.service_id != allocation.service_id
            or delivery.service_type != allocation.service_type
        ):
            raise ValueError(
                f"Delivery does not match allocation: {delivery.demand_id}"
            )

        delivery_lookup[delivery.demand_id] = delivery

    allocated_count = sum(
        allocation.allocation_status == "allocated"
        for allocation in allocations
    )

    unallocated_count = len(allocations) - allocated_count

    attended_count = sum(
        delivery.attendance_status == "attended"
        for delivery in deliveries
    )

    did_not_attend_count = sum(
        delivery.attendance_status == "did_not_attend"
        for delivery in deliveries
    )

    delivered_count = sum(
        delivery.delivery_status == "delivered"
        for delivery in deliveries
    )

    not_delivered_count = sum(
        delivery.delivery_status == "not_delivered"
        for delivery in deliveries
    )

    return ServiceDeliveryAssessment(
        requested_count=len(demands),
        allocated_count=allocated_count,
        unallocated_count=unallocated_count,
        attendance_recorded_count=len(deliveries),
        attended_count=attended_count,
        did_not_attend_count=did_not_attend_count,
        delivery_recorded_count=len(deliveries),
        delivered_count=delivered_count,
        not_delivered_count=not_delivered_count,
        pending_delivery_count=allocated_count - len(deliveries),
    )
