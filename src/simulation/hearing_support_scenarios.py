"""Illustrative six-month hearing-support scenarios.

These scenarios demonstrate different pathways from reported
functional difficulty to perceived need, help-seeking and service access.

All scenario values are explicit simulation assumptions.
No behavioural probabilities or population estimates are used.
"""

from src.agents.agent import Agent, AgentProfile
from src.hearing_support.need import HearingSupportNeed
from src.hearing_support.service_access import ServiceAccess
from src.population.integration import create_hearing_support_records


EVIDENCE = "simulation_assumption"


def add_need(record, month, perceived, intention, action):
    """Add a time-specific hearing-support assessment."""

    need = HearingSupportNeed(
        agent_id=record.agent_id,
        assessment_month=month,
        functional_difficulty_status="difficulty_reported",
        perceived_need=perceived,
        help_seeking_intention=intention,
        help_seeking_action=action,
        evidence_status=EVIDENCE,
    )

    record.add_hearing_support_need(need)


def build_scenarios():
    """Build three illustrative individual hearing-support pathways."""

    scenario_definitions = [
        {
            "agent_id": "SCENARIO-A",
            "description": (
                "Recognises a need and contacts an available service."
            ),
        },
        {
            "agent_id": "SCENARIO-B",
            "description": (
                "Reports difficulty but does not recognise a need."
            ),
        },
        {
            "agent_id": "SCENARIO-C",
            "description": (
                "Recognises a need and contacts a service, "
                "but encounters an access barrier."
            ),
        },
    ]

    agents = [
        Agent(
            agent_id=item["agent_id"],
            profile=AgentProfile(
                age_group="unknown",
                hearing_profile="unknown",
                geography="unknown",
                auditory_functional_status="difficulty_reported",
            ),
        )
        for item in scenario_definitions
    ]

    records = create_hearing_support_records(agents)
    records_by_id = {record.agent_id: record for record in records}

    # Month 1: all three individuals report functional difficulty.
    for record in records:
        add_need(
            record,
            month=1,
            perceived="unknown",
            intention="unknown",
            action="no_action",
        )

    # Month 3: their recognition and intentions differ.
    add_need(
        records_by_id["SCENARIO-A"],
        month=3,
        perceived="yes",
        intention="yes",
        action="no_action",
    )

    add_need(
        records_by_id["SCENARIO-B"],
        month=3,
        perceived="no",
        intention="no",
        action="no_action",
    )

    add_need(
        records_by_id["SCENARIO-C"],
        month=3,
        perceived="yes",
        intention="yes",
        action="no_action",
    )

    # Month 6: record the subsequent help-seeking actions.
    add_need(
        records_by_id["SCENARIO-A"],
        month=6,
        perceived="yes",
        intention="yes",
        action="service_contacted",
    )

    add_need(
        records_by_id["SCENARIO-B"],
        month=6,
        perceived="no",
        intention="no",
        action="no_action",
    )

    add_need(
        records_by_id["SCENARIO-C"],
        month=6,
        perceived="yes",
        intention="yes",
        action="service_contacted",
    )

    # Service access is recorded separately from help-seeking action.
    records_by_id["SCENARIO-A"].add_service_access(
        ServiceAccess(
            agent_id="SCENARIO-A",
            service_type="audiology_assessment",
            pathway="unknown",
            availability_status="available",
            appointment_status="requested",
            attendance_status="not_yet_due",
            evidence_status=EVIDENCE,
        )
    )

    records_by_id["SCENARIO-C"].add_service_access(
        ServiceAccess(
            agent_id="SCENARIO-C",
            service_type="audiology_assessment",
            pathway="unknown",
            availability_status="unavailable",
            appointment_status="not_available",
            attendance_status="not_yet_due",
            evidence_status=EVIDENCE,
        )
    )

    for record in records:
        record.validate()

    return records, scenario_definitions


def print_scenarios():
    """Display the scenario histories and service-access outcomes."""

    records, definitions = build_scenarios()
    descriptions = {
        item["agent_id"]: item["description"]
        for item in definitions
    }

    print("\nSIX-MONTH HEARING-SUPPORT SCENARIOS")
    print("=" * 65)
    print("Illustrative assumptions only — not population estimates.")

    for record in records:
        print(f"\n{record.agent_id}")
        print("-" * 65)
        print(descriptions[record.agent_id])

        print("\nNeed and help-seeking history:")

        for need in sorted(
            record.hearing_support_needs,
            key=lambda item: item.assessment_month,
        ):
            print(
                f"  Month {need.assessment_month}: "
                f"difficulty={need.functional_difficulty_status}, "
                f"perceived_need={need.perceived_need}, "
                f"intention={need.help_seeking_intention}, "
                f"action={need.help_seeking_action}"
            )

        print("\nService access:")

        if not record.service_access_records:
            print("  No service access record.")
        else:
            for service in record.service_access_records:
                print(
                    f"  Service: {service.service_type}\n"
                    f"  Availability: {service.availability_status}\n"
                    f"  Appointment: {service.appointment_status}\n"
                    f"  Attendance: {service.attendance_status}"
                )

    print("\n" + "=" * 65)
    print(f"Individuals: {len(records)}")
    print(
        "Need assessments:",
        sum(len(r.hearing_support_needs) for r in records),
    )
    print(
        "Service access records:",
        sum(len(r.service_access_records) for r in records),
    )
    print("All individual records validated successfully.")


if __name__ == "__main__":
    print_scenarios()
