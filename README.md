# Chrysalis

A metamorphic testing framework that utilizes metamorphic relations.

## What is Metamorphic Testing?

Metamorphic testing is a software testing technique that focuses on relations between multiple executions of a program. Instead of checking if a program produces the "correct" output for a given input (which may be unknown) metamorphic testing verifies that certain relationships hold between inputs and their corresponding outputs.

## Core Concepts

**System Under Test (SUT)** - The function or system to test.

**Transformations** - Functions that modify the input data while preserving certain properties.

**Invariants** - Predicates that define relationships between outputs.

**Metamorphic Relations** - The combination of a transformation and invariant that defines a testable property of a system.

## Installation

```bash
pip install chrysalis-test
```

## Usage

### Registering Relations

Use `chry.register()` to register metamorphic relations by combining transformations and invariants:

```python
import chrysalis as chry

chry.register(
    transformation=transformation_function,
    invariant=chry.invariants.equals
)
```

### Running Tests

Use `chry.run()` to execute metamorphic testing on your system under test:

```python
results = chry.run(
    sut=sut_function,
    input_data=test_data,
    chain_length=10,
    num_chains=20
)
```

## Official Documentation

[Chrysalis - A metamorphic testing framework that utilizes metamorphic relations to detect bugs.](https://chrysalis-test.github.io/Chrysalis/index.html)

## Development

For development, use the following commands:

- Format and check code: `./scripts/format_and_check.sh`
- Run unit tests: `uv run pytest`
- Run integration test: `python3 -m tests_integration.sql`
- Build docs: `./scripts/build_docs.sh`
