# Australian Hearing Health Population Simulator

An agent-based simulation project exploring hearing health, communication experiences, access to hearing support, service capacity and individual care pathways in Australia.

## Overview

The Australian Hearing Health Population Simulator is a research and scenario-exploration project designed to examine how individual circumstances, communication experiences, hearing support needs, service availability and interventions may interact over time.

The project uses synthetic individuals (agents) to represent different population characteristics and experiences. Agents can have different age groups, hearing profiles, functional difficulties, geographical circumstances, communication profiles and relationships.

The simulator aims to support structured exploration of questions such as:

- How might geographical barriers affect access to hearing assessment and support?
- How might service capacity, workforce availability and operational costs influence service delivery?
- How do communication difficulties affect individual experiences and relationships?
- How might funding arrangements and personal contributions influence access to care?
- How could interventions and changes to service delivery affect individual hearing-care pathways?

The project is under active development.

## Research and modelling principles

The simulator follows several important principles.

### Hearing-aid ownership is not a measure of successful hearing care

The model distinguishes between:

- Access to hearing assessment and services
- Suitability of available support
- Acquisition of hearing devices or other support
- Actual use of support
- Functional effectiveness
- Individual satisfaction and longer-term outcomes

Ownership does not automatically imply use or benefit. Similarly, not owning a hearing aid does not necessarily mean that an individual has received unsuccessful care.

### Hearing ability and functional communication are distinct

A hearing profile alone does not determine an individual's communication experience.

People with normal audiometric profiles may still report functional hearing or communication difficulties. The simulator therefore distinguishes hearing profiles from reported and confirmed functional difficulties.

### Unknown information remains unknown

Missing information is not automatically interpreted as a negative outcome or absence of difficulty.

### Evidence and assumptions are distinguished

Model information is classified using evidence-status concepts, including:

- Evidence-supported
- Simulation assumption
- Not yet established

Synthetic population characteristics and illustrative assumptions must not be interpreted as measured Australian population estimates.

## Main components

| Component | Purpose |
|---|---|
| Population | Generates synthetic individuals and integrates population records. |
| Agents | Represents individual profiles, states, relationships and memory. |
| Communication | Models communication environments, events and communication experiences. |
| Behaviour | Represents individual experiences and relationship changes. |
| Hearing support | Models support needs, funding arrangements, service access and care journeys. |
| Service capacity | Represents workforce, geographic access, costs, funding and operational capacity. |
| Service delivery | Models service demand, allocation, assessment and delivery. |
| Interventions | Loads and represents configurable interventions. |
| Simulation | Runs longitudinal demonstrations and hearing-support scenarios. |

## Optional local language-model integration

The project includes an experimental local LLM communication interpretation module.

It uses Ollama to access a locally installed language model.

Current characteristics:

- LLM integration is optional and disabled by default.
- The current default model is `qwen3:1.7b`.
- Individual participant requests are handled separately.
- Generated interpretations are explicitly marked as unverified.
- LLM output does not directly modify agent states, relationships, clinical status or simulation outcomes.
- The simulation remains controlled by Python logic.

The LLM integration is experimental. Structurally valid model output should not be interpreted as factually or clinically validated.

## Technology

- Python 3.11+
- SQLite for simulation memory and event storage
- `pytest` for automated testing
- Ollama for optional local language-model experimentation

The application currently uses Python standard-library modules. No external runtime Python packages are required by the modules inspected so far. `pytest` is required to run the test suite.

## Project structure

```text
Australian_Hearing_Health_Simulator/
│
├── config/
│   ├── HH-EXP-001.json
│   ├── communication_vocabulary.json
│   └── population_baseline.synthetic.json
│
├── documentation/
│   ├── communication_vocabulary.md
│   ├── hearing_support_and_funding_model.md
│   └── Hearing Support Access and Individual.docx
│
├── outputs/
│   └── SQLite simulation databases
│
├── src/
│   ├── agents/
│   ├── behaviour/
│   ├── communication/
│   ├── hearing_support/
│   ├── interventions/
│   ├── population/
│   ├── service_capacity/
│   ├── service_delivery/
│   └── simulation/
│
└── tests/
    └── Automated test suite
```

## Installation

Clone the repository:

```bash
git clone git@github.com:Olynmpus/Australian_Hearing_Health_Simulator.git
cd Australian_Hearing_Health_Simulator
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on Linux or WSL:

```bash
source .venv/bin/activate
```

Install the test dependency:

```bash
python -m pip install pytest
```

## Running the tests

From the project root:

```bash
python -m pytest -q
```

The test suite covers population generation, agents, communication, relationships, hearing support, funding, service access, service capacity, service delivery, interventions and simulation integration.

## Running the longitudinal demonstration

The longitudinal demonstration can be started with:

```bash
python -m src.simulation.longitudinal_demo
```

By default, the demonstration writes to:

```text
outputs/HH-EXP-001-longitudinal-demo-v2.db
```

The application protects existing databases and stops if the selected output database already exists. Use a new output path when running another experiment rather than overwriting previous results.

## Current development status

The project is actively evolving.

Current implementation areas include:

- Synthetic population generation
- Individual agent profiles and state
- Communication events and participant perspectives
- Relationships and individual memory histories
- Hearing support needs and individual support records
- Funding and service access representation
- Service capacity and delivery modelling
- Longitudinal simulation
- Optional local LLM communication interpretation

Further development is required to calibrate assumptions against appropriate evidence, validate model behaviour and establish the suitability of different scenarios for research or policy exploration.

## Limitations

This project is not currently:

- A calibrated representation of the Australian population.
- A validated epidemiological or clinical prediction model.
- A clinical diagnostic or treatment recommendation system.
- Evidence that a particular policy or intervention will produce a specific real-world outcome.

Simulation outputs depend on the assumptions, parameters and mechanisms implemented in the model. Results should be interpreted as exploratory outputs rather than predictions of actual Australian hearing health outcomes.

## Research direction

The longer-term objective is to develop an interactive educational and scenario-exploration platform.

Users should be able to describe hearing-health scenarios in ordinary language, explore controlled baseline and intervention simulations, and examine the resulting changes alongside assumptions, uncertainty, limitations and potential unintended consequences.

AI may assist with interpreting questions and explaining results. The underlying Python simulation remains responsible for generating authoritative model outcomes.

## Licence

No licence has currently been specified for this repository.
