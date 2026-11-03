"""Integration between generated agents and hearing-support records."""

from src.agents.agent import Agent
from src.hearing_support.individual_record import (
    IndividualHearingSupportRecord,
)


def create_hearing_support_records(agents):
    """Create one empty hearing-support record for each generated agent.

    No funding eligibility, service need, service availability or
    care journey is inferred.
    """

    if not isinstance(agents, list):
        raise ValueError("agents must be a list.")

    records = []
    seen_ids = set()

    for agent in agents:
        if not isinstance(agent, Agent):
            raise ValueError("Every item must be an Agent.")

        agent.validate()

        if agent.agent_id in seen_ids:
            raise ValueError(
                f"Duplicate agent ID: {agent.agent_id}"
            )

        seen_ids.add(agent.agent_id)

        records.append(
            IndividualHearingSupportRecord(agent=agent)
        )

    return records
