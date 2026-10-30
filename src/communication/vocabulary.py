"""Load and validate the hearing-health communication vocabulary."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VocabularyTerm:
    """A single controlled vocabulary term."""

    term_id: str
    label: str
    definition: str
    domain_id: str


class CommunicationVocabulary:
    """Load, validate and retrieve communication vocabulary terms."""

    def __init__(self, vocabulary_id, version, status, terms_by_id,
                 terms_by_domain):
        self.vocabulary_id = vocabulary_id
        self.version = version
        self.status = status
        self._terms_by_id = terms_by_id
        self._terms_by_domain = terms_by_domain

    @classmethod
    def from_file(cls, file_path):
        """Load a vocabulary from a JSON file."""

        path = Path(file_path)

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        required_metadata = (
            "vocabulary_id",
            "version",
            "status",
            "domains",
        )

        for key in required_metadata:
            if key not in data:
                raise ValueError(
                    f"Missing required vocabulary field: {key}"
                )

        if not isinstance(data["domains"], list):
            raise ValueError("'domains' must be a list.")

        terms_by_id = {}
        terms_by_domain = {}
        domain_ids = set()

        for domain in data["domains"]:
            if not isinstance(domain, dict):
                raise ValueError("Each domain must be an object.")

            domain_id = domain.get("id")
            domain_terms = domain.get("terms")

            if not isinstance(domain_id, str) or not domain_id.strip():
                raise ValueError("Every domain needs a valid ID.")

            if domain_id in domain_ids:
                raise ValueError(
                    f"Duplicate domain identifier: {domain_id}"
                )

            if not isinstance(domain_terms, list):
                raise ValueError(
                    f"Terms for domain '{domain_id}' must be a list."
                )

            domain_ids.add(domain_id)
            terms_by_domain[domain_id] = []

            for record in domain_terms:
                if not isinstance(record, list) or len(record) != 3:
                    raise ValueError(
                        f"Invalid term record in domain '{domain_id}'."
                    )

                term_id, label, definition = record

                values = (term_id, label, definition)

                if not all(
                    isinstance(value, str) and value.strip()
                    for value in values
                ):
                    raise ValueError(
                        f"Invalid term fields in domain '{domain_id}'."
                    )

                if term_id in terms_by_id:
                    raise ValueError(
                        f"Duplicate vocabulary identifier: {term_id}"
                    )

                term = VocabularyTerm(
                    term_id=term_id,
                    label=label,
                    definition=definition,
                    domain_id=domain_id,
                )

                terms_by_id[term_id] = term
                terms_by_domain[domain_id].append(term)

        return cls(
            vocabulary_id=data["vocabulary_id"],
            version=data["version"],
            status=data["status"],
            terms_by_id=terms_by_id,
            terms_by_domain=terms_by_domain,
        )

    def get_term(self, term_id):
        """Retrieve a term by its unique identifier."""

        if term_id not in self._terms_by_id:
            raise KeyError(
                f"Unknown vocabulary identifier: {term_id}"
            )

        return self._terms_by_id[term_id]

    def has_term(self, term_id):
        """Check whether an identifier exists."""

        return term_id in self._terms_by_id

    def get_domain_terms(self, domain_id):
        """Retrieve all terms belonging to a domain."""

        if domain_id not in self._terms_by_domain:
            raise KeyError(
                f"Unknown vocabulary domain: {domain_id}"
            )

        return tuple(self._terms_by_domain[domain_id])

    @property
    def term_count(self):
        """Return the total number of vocabulary terms."""

        return len(self._terms_by_id)
