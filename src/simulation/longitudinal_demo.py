from pathlib import Path

from src.agents.agent import Agent, AgentProfile, AgentState, AgentCommunicationProfile
from src.agents.memory_store import MemoryStore
from src.agents.relationships import SocialRelationship
from src.behaviour.experience_model import apply_experience
from src.behaviour.relationship_model import apply_relationship_experience
from src.behaviour.communication_model import (
    CommunicationEvent,
    CommunicationEnvironment,
)
from src.behaviour.llm_interpreter import (
    interpret_interaction,
    DEFAULT_MODEL,
)


def run_experiment(database_path, enable_llm=False):
    """Run a four-month illustrative longitudinal experiment."""

    database_path = Path(database_path)

    if database_path.exists():
        raise FileExistsError(
            f"Database already exists: {database_path}. "
            "Choose another path to avoid overwriting it."
        )

    agents = {
        "PERSON-001": Agent(
            agent_id="PERSON-001",
            profile=AgentProfile(
                age_group="working_age_adult",
                hearing_profile="moderate_hearing_difficulty",
                geography="regional",
                role="community_member",
                onset_type="acquired",
                progression_type="stable",
                communication_profile=AgentCommunicationProfile(
                    modalities=["spoken_communication"]
                ),
            ),
            state=AgentState(),
            history_id="PERSON-001",
        ),

        "FAMILY-001": Agent(
            agent_id="FAMILY-001",
            profile=AgentProfile(
                age_group="working_age_adult",
                hearing_profile="unknown",
                geography="regional",
                role="family_member",
            ),
            state=AgentState(),
            history_id="FAMILY-001",
        ),

        "FRIEND-001": Agent(
            agent_id="FRIEND-001",
            profile=AgentProfile(
                age_group="working_age_adult",
                hearing_profile="unknown",
                geography="regional",
                role="friend",
            ),
            state=AgentState(),
            history_id="FRIEND-001",
        ),

        "SERVICE-001": Agent(
            agent_id="SERVICE-001",
            profile=AgentProfile(
                age_group="working_age_adult",
                hearing_profile="unknown",
                geography="regional",
                role="service_representative",
            ),
            state=AgentState(),
            history_id="SERVICE-001",
        ),
    }

    person = agents["PERSON-001"]

    for agent in agents.values():
        agent.validate()

    relationships = {
        "PERSON-001": {
            "FAMILY-001": SocialRelationship(
                agent_id="PERSON-001",
                contact_id="FAMILY-001",
                relationship_type="family",
            ),
            "SERVICE-001": SocialRelationship(
                agent_id="PERSON-001",
                contact_id="SERVICE-001",
                relationship_type="health_service",
            ),
            "FRIEND-001": SocialRelationship(
                agent_id="PERSON-001",
                contact_id="FRIEND-001",
                relationship_type="friend",
            ),
        },
        "FAMILY-001": {
            "PERSON-001": SocialRelationship(
                agent_id="FAMILY-001",
                contact_id="PERSON-001",
                relationship_type="family",
            ),
        },
        "SERVICE-001": {
            "PERSON-001": SocialRelationship(
                agent_id="SERVICE-001",
                contact_id="PERSON-001",
                relationship_type="client",
            ),
        },
        "FRIEND-001": {
            "PERSON-001": SocialRelationship(
                agent_id="FRIEND-001",
                contact_id="PERSON-001",
                relationship_type="friend",
            ),
        },
    }

    for agent_id, agent_relationships in relationships.items():
        if agent_id not in agents:
            raise ValueError("Relationship owner does not exist.")

        for relationship in agent_relationships.values():
            relationship.validate()

            if relationship.agent_id != agent_id:
                raise ValueError("Relationship owner does not match its key.")

            if relationship.contact_id not in agents:
                raise ValueError("Relationship contact does not exist.")

    monthly_events = [
        {
            "month": 1,
            "interaction_id": "INTERACTION-001",
            "event_type": "family_interaction",
            "participants": ["PERSON-001", "FAMILY-001"],
            "message": "A family conversation was difficult to follow.",
            "perspectives": {
                "PERSON-001": {
                    "interpretation": "The person felt excluded from the conversation.",
                    "outcome": "negative_communication",
                    "perspective_type": "recipient",
                },
                "FAMILY-001": {
                    "interpretation": "The family member noticed communication difficulties during the conversation.",
                    "outcome": None,
                    "perspective_type": "other_participant",
                },
            },
        },
        {
             "month": 2,
            "interaction_id": "INTERACTION-002",
            "event_type": "service_interaction",
            "participants": ["PERSON-001", "SERVICE-001"],
            "message": "The person received information that did not address their needs.",
            "perspectives": {
                "PERSON-001": {
                    "interpretation": "The person felt uncertain about where to seek help.",
                    "outcome": "misdirected_information",
                    "perspective_type": "recipient",
                },
                "SERVICE-001": {
                    "interpretation": "The service representative's understanding of the interaction has not yet been established.",
                    "outcome": None,
                    "perspective_type": "other_participant",
                },
            },
        },
        {
            "month": 3,
            "interaction_id": "INTERACTION-003",
            "event_type": "social_interaction",
            "participants": ["PERSON-001", "FRIEND-001"],
            "message": "A friend made an effort to communicate clearly.",
            "perspectives": {
                "PERSON-001": {
                    "interpretation": "The person felt included and supported.",
                    "outcome": "supportive_communication",
                    "perspective_type": "recipient",
                },
                "FRIEND-001": {
                    "interpretation": "The friend attempted to make communication easier.",
                    "outcome": None,
                    "perspective_type": "other_participant",
                },
            },
        },
        {
            "month": 4,
            "interaction_id": "INTERACTION-004",
            "event_type": "service_interaction",
            "participants": ["PERSON-001", "SERVICE-001"],
            "message": "The person encountered a barrier when trying to access a service.",
            "perspectives": {
                "PERSON-001": {
                    "interpretation": "The person felt discouraged about accessing support.",
                    "outcome": "blocked_service_access",
                    "perspective_type": "recipient",
                },
                "SERVICE-001": {
                    "interpretation": "The service representative's understanding of the access barrier has not yet been established.",
                    "outcome": None,
                    "perspective_type": "other_participant",
                },
            },
        },
    ]

    snapshots = []

    memory = MemoryStore(database_path)

    for event in monthly_events:
        month = event["month"]
        participants = event["participants"]
        communication_event = CommunicationEvent(
            speaker_id=participants[1],
            listener_id=participants[0],
            intended_message=event["message"],
            perceived_message=None,
            listener_interpretation=None,
            channel="speech",
            environment=CommunicationEnvironment(),
        )

        communication_event.validate()

        llm_results = {}

        if enable_llm and event["interaction_id"] == "INTERACTION-001":
            for participant_id in participants:
                participant_role = (
                    event["perspectives"][participant_id]["perspective_type"]
                )

                try:
                    result = interpret_interaction(
                        agent_id=participant_id,
                        interaction_context={
                            "event_type": event["event_type"],
                            "event_description": event["message"],
                            "participant_role": participant_role,
                        },
                    )

                    llm_results[participant_id] = {
                        "text": result.text,
                        "source": "local_llm",
                        "model": result.model,
                        "evidence_status": "model_generated_unverified",
                        "verified": False,
                        "status": result.status,
                        "error": result.error,
                    }

                except Exception as exc:
                    llm_results[participant_id] = {
                        "text": None,
                        "source": "local_llm",
                        "model": DEFAULT_MODEL,
                        "evidence_status": "model_generated_unverified",
                        "verified": False,
                        "status": "failed",
                        "error": str(exc),
                    }

        for agent_id in participants:
            agent = agents[agent_id]
            other_participant = next(
                participant
                for participant in participants
                if participant != agent_id
            )

            agent.current_month = month

            perspective = event["perspectives"][agent_id]
            outcome = perspective["outcome"]

            state_changes = {}
            relationship_changes = {}

            if outcome is not None:
                state_changes = apply_experience(
                    agent.state,
                    outcome,
                )

                relationship = relationships[agent_id][other_participant]

                relationship_changes = apply_relationship_experience(
                    relationship,
                    outcome,
                )

            memory.record_event(
                agent_id=agent_id,
                month=month,
                event_type=event["event_type"],
                actual_message=event["message"],
                agent_interpretation=perspective["interpretation"],
                outcome=outcome or "not_assigned",
                additional_details={
                    "interaction_id": event["interaction_id"],
                    "participants": participants,
                    "communication_event": {
                        "speaker_id": communication_event.speaker_id,
                        "listener_id": communication_event.listener_id,
                        "intended_message": communication_event.intended_message,
                        "perceived_message": communication_event.perceived_message,
                        "listener_interpretation": (
                            communication_event.listener_interpretation
                        ),
                        "channel": communication_event.channel,
                        "initial_outcome": communication_event.initial_outcome,
                        "final_outcome": communication_event.final_outcome,
                    },
                    "perspective_type": perspective["perspective_type"],
                    "state_changes": state_changes,
                    "relationship_changes": relationship_changes,
                    "interpretation_provenance": {
                        "source": "scenario_script",
                        "evidence_status": "simulation_assumption",
                        "verified": False,
                    },
                    "llm_interpretation": llm_results.get(
                        agent_id,
                        {
                            "text": None,
                            "source": "local_llm",
                            "model": None,
                            "evidence_status": "model_generated_unverified",
                            "verified": False,
                            "status": "not_generated",
                            "error": None,
                        },
                    ),
                },
            )

        snapshots.append(
            {
                "month": month,
                "outcome": event["perspectives"][person.agent_id]["outcome"],
                "state": person.summary(),
            }
        )

    agent_histories = {
        agent_id: memory.get_history(agent_id)
        for agent_id in agents
    }

    return person, relationships, agent_histories, snapshots


if __name__ == "__main__":
    output_path = Path("outputs/HH-EXP-001-longitudinal-demo-v2.db")

    try:
        person, relationships, history, snapshots = run_experiment(
            output_path
        )
    except FileExistsError as error:
        raise SystemExit(str(error))

    print("\nLONGITUDINAL EXPERIMENT")
    print("======================")

    for snapshot in snapshots:
        print(f"\nMonth {snapshot['month']}: {snapshot['outcome']}")
        for key, value in snapshot["state"].items():
            print(f"  {key}: {value}")

    print("\nFINAL RELATIONSHIPS")
    print("==================")

    for agent_id, agent_relationships in relationships.items():
        print(f"\n{agent_id}")

        for contact_id, relationship in agent_relationships.items():
            print(
                f"  {contact_id}: "
                f"trust={relationship.trust:.2f}, "
                f"support={relationship.perceived_support:.2f}"
            )

    print("\nAGENT MEMORY HISTORIES")
    print("======================")

    for agent_id, events in history.items():
        print(f"{agent_id}: {len(events)} events")

    total_events = sum(len(events) for events in history.values())
    print(f"\nTotal memory events: {total_events}")
    print(f"Database saved at: {output_path}")