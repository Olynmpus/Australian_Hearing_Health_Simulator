import json
import sqlite3

from pathlib import Path


class MemoryStore:
    """Persistent storage for individual agent experiences."""

    def __init__(self, database_path="outputs/agent_memory.db"):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def initialize(self):
        """Create the interaction history table if it does not exist."""

        with sqlite3.connect(self.database_path) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS interaction_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    month INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    sender_id TEXT,
                    recipient_id TEXT,
                    actual_message TEXT,
                    agent_interpretation TEXT,
                    outcome TEXT NOT NULL,
                    source_accuracy REAL,
                    emotional_appraisal TEXT,
                    additional_details TEXT
                )
            """)

    def record_event(
        self,
        agent_id,
        month,
        event_type,
        outcome,
        sender_id=None,
        recipient_id=None,
        actual_message=None,
        agent_interpretation=None,
        source_accuracy=None,
        emotional_appraisal=None,
        additional_details=None,
    ):
        """Save one experience to an agent's persistent history."""

        if not agent_id:
            raise ValueError("Agent ID cannot be empty.")

        if month < 0:
            raise ValueError("Month cannot be negative.")

        if source_accuracy is not None:
            if not 0.0 <= source_accuracy <= 1.0:
                raise ValueError("Source accuracy must be between 0 and 1.")

        details_json = json.dumps(
            additional_details or {},
            ensure_ascii=False
        )

        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.execute("""
                INSERT INTO interaction_events (
                    agent_id,
                    month,
                    event_type,
                    sender_id,
                    recipient_id,
                    actual_message,
                    agent_interpretation,
                    outcome,
                    source_accuracy,
                    emotional_appraisal,
                    additional_details
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent_id,
                month,
                event_type,
                sender_id,
                recipient_id,
                actual_message,
                agent_interpretation,
                outcome,
                source_accuracy,
                emotional_appraisal,
                details_json,
            ))

            return cursor.lastrowid

    def get_history(self, agent_id, limit=None):
        """Retrieve an agent's events in chronological order."""

        query = """
            SELECT *
            FROM interaction_events
            WHERE agent_id = ?
            ORDER BY month ASC, event_id ASC
        """

        parameters = [agent_id]

        if limit is not None:
            if limit < 1:
                raise ValueError("Limit must be at least 1.")

            query += " LIMIT ?"
            parameters.append(limit)

        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                query, parameters
            ).fetchall()

        events = []

        for row in rows:
            event = dict(row)
            event["additional_details"] = json.loads(
                event["additional_details"]
            )
            events.append(event)

        return events
