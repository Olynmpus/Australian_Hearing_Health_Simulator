from pathlib import Path

from src.agents.agent import Agent, AgentProfile, AgentState, AgentCommunicationProfile
from src.agents.memory_store import MemoryStore
from src.agents.relationships import SocialRelationship
from src.behaviour.experience_model import apply_experience
from src.behaviour.relationship_model import apply_relationship_experience


def run_experiment(database_path):
    """Run a four-month illustrative longitudinal experiment."""

    database_path = Path(database_path)

    if database_path.exists():
        raise FileExistsError(
            f"Database already exists: {database_path}. "
            "Choose another path to avoid overwriting it."
        )

    person = Agent(
        agent_id="PERSON-001",
        profile=AgentProfile(
            age_group="working_age_adult",
            hearing_profile="moderate_hearing_difficulty",
            geography="regional",
            role="community_member",
            onset_type="acquired",
            progression_type="stable",
            communication_profile=AgentCommunicationProfile(modalities=["spoken_communication"]),
        ),
        state=AgentState(),
        current_month=0,
        history_id="PERSON-001",
    )

    relationships = {
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
    }

    monthly_events = [
        {
            "month": 1,
            "contact": "FAMILY-001",
            "event_type": "family_interaction",
            "outcome": "negative_communication",
            "message": "A family conversation was difficult to follow.",
            "interpretation": "The person felt excluded from the conversation.",
        },
        {
            "month": 2,
            "contact": "SERVICE-001",
            "event_type": "service_interaction",
            "outcome": "misdirected_information",
            "message": "The person received information that did not address their needs.",
            "interpretation": "The person felt uncertain about where to seek help.",
        },
        {
            "month": 3,
            "contact": "FRIEND-001",
            "event_type": "social_interaction",
            "outcome": "supportive_communication",
            "message": "A friend made an effort to communicate clearly.",
            "interpretation": "The person felt included and supported.",
        },
        {
            "month": 4,
            "contact": "SERVICE-001",
            "event_type": "service_interaction",
            "outcome": "blocked_service_access",
            "message": "The person encountered a barrier when trying to access a service.",
            "interpretation": "The person felt discouraged about accessing support.",
        },
    ]

    snapshots = []

    memory = MemoryStore(database_path)
    for event in monthly_events:
        person.current_month = event["month"]

        state_changes = apply_experience(
            person.state,
            event["outcome"],
        )

        relationship = relationships[event["contact"]]

        relationship_changes = apply_relationship_experience(
            relationship,
            event["outcome"],
        )

        memory.record_event(
            agent_id=person.agent_id,
            month=event["month"],
            event_type=event["event_type"],
            sender_id=event["contact"],
            recipient_id=person.agent_id,
            actual_message=event["message"],
            agent_interpretation=event["interpretation"],
            outcome=event["outcome"],
            source_accuracy=None,
            emotional_appraisal=None,
            additional_details={
                "state_changes": state_changes,
                "relationship_changes": relationship_changes,
            },
         )

        snapshots.append(
            {
                "month": event["month"],
                "outcome": event["outcome"],
                "state": person.summary(),
            }
        )

    history = memory.get_history(person.agent_id)

    return person, relationships, history, snapshots


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

    for contact_id, relationship in relationships.items():
        print(
            f"{contact_id}: "
            f"trust={relationship.trust:.2f}, "
            f"support={relationship.perceived_support:.2f}"
        )

    print(f"\nRetrieved history events: {len(history)}")
    print(f"Database saved at: {output_path}")