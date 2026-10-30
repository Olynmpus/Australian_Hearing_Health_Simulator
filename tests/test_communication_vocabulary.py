"""Tests for the communication vocabulary loader."""

import json
from pathlib import Path

import pytest

from src.communication.vocabulary import CommunicationVocabulary


PROJECT_ROOT = Path(__file__).resolve().parents[1]

VOCABULARY_PATH = (
    PROJECT_ROOT / "config" / "communication_vocabulary.json"
)


def test_load_project_vocabulary():
    vocabulary = CommunicationVocabulary.from_file(VOCABULARY_PATH)

    assert vocabulary.vocabulary_id == "AUS_HH_COMM_VOCAB"
    assert vocabulary.version == "0.1.0"
    assert vocabulary.term_count == 149


def test_retrieve_spoken_communication_modality():
    vocabulary = CommunicationVocabulary.from_file(VOCABULARY_PATH)

    term = vocabulary.get_term("spoken_communication")

    assert term.domain_id == "communication_modalities"
    assert term.label == "Spoken communication"


def test_retrieve_spoken_communication_preference():
    vocabulary = CommunicationVocabulary.from_file(VOCABULARY_PATH)

    term = vocabulary.get_term("prefers_spoken_communication")

    assert term.domain_id == "spoken_auditory_preferences"


def test_check_existing_identifier():
    vocabulary = CommunicationVocabulary.from_file(VOCABULARY_PATH)

    assert vocabulary.has_term("face_to_face") is True


def test_check_unknown_identifier():
    vocabulary = CommunicationVocabulary.from_file(VOCABULARY_PATH)

    assert vocabulary.has_term("unknown_term") is False


def test_unknown_term_raises_error():
    vocabulary = CommunicationVocabulary.from_file(VOCABULARY_PATH)

    with pytest.raises(KeyError):
        vocabulary.get_term("unknown_term")


def test_retrieve_domain_terms():
    vocabulary = CommunicationVocabulary.from_file(VOCABULARY_PATH)

    terms = vocabulary.get_domain_terms(
        "communication_modalities"
    )

    assert len(terms) == 12
    assert all(
        term.domain_id == "communication_modalities"
        for term in terms
    )


def test_duplicate_identifiers_are_rejected(tmp_path):
    data = {
        "vocabulary_id": "TEST",
        "version": "0.1",
        "status": "draft",
        "domains": [
            {
                "id": "domain_a",
                "terms": [["shared_id", "First", "First definition"]]
            },
            {
                "id": "domain_b",
                "terms": [["shared_id", "Second", "Second definition"]]
            },
        ],
    }

    path = tmp_path / "duplicate.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="Duplicate vocabulary"):
        CommunicationVocabulary.from_file(path)
