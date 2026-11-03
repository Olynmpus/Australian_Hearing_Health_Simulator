"""Population generation and integration for the hearing-health simulator."""

from src.population.generator import generate_population
from src.population.integration import create_hearing_support_records

__all__ = [
    "generate_population",
    "create_hearing_support_records",
]
