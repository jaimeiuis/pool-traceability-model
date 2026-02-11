# Pooling/Reflex Traceability Model (SQLite)

This project demonstrates a minimal, queryable traceability model for pooled testing with reflex retesting. It ingests a QC’d intake contract (`clean_intake.csv`) produced by Project #1 and supports lineage + exception detection queries in SQLite.

Together with Project #1, this forms a simple two-stage pipeline:
- **Stage 1 (Project #1):** validate/normalize intake + exception reporting (`clean_intake.csv`)
- **Stage 2 (this repo):** load into SQLite + traceability lineage + exception queries

## Problem
Some lab workflows require pooled testing with reflex retesting, but systems may not natively support parent/child traceability (pool ↔ constituent samples) and exception routing.

## Solution
This project models the workflow in SQLite with:
- pools and membership (pool ↔ sample mapping)
- pool-level test results
- reflex tests for constituent samples
- lineage queries and exception detection (e.g., missing reflex tests)

## Key outputs
- sample-level lineage view (pool result + reflex result)
- exception report query (missing reflex / inconsistent state)
- derived final status logic (e.g., FINAL_NEG vs PENDING_REFLEX)

## Upstream dependency (Project #1)
This project expects a load-ready intake contract (`clean_intake.csv`) produced by the upstream QC pipeline. The QC stage ensures identifier integrity and provides an audit-friendly exceptions log so downstream lineage queries remain reliable.

Upstream repo: https://github.com/jaimeiuis/intake-qc-pipeline

## Usage (load QC’d intake from Project #1)
1) Generate the intake contract in Project #1:
- Output: `outputs/clean_intake.csv`

2) Load the intake contract into the traceability database:
```bash
pip install -r requirements.txt
python src/load_intake.py --clean-intake ../intake-qc-pipeline/outputs/clean_intake.csv
```

## Images

Query result screenshots (see [images/](images/)):

| Query | Description | Screenshot |
|-------|--------------|------------|
| **A** | Pool membership | [images/pool_membership.png](images/pool_membership.png) |
| **B** | Pools that triggered reflex testing | [images/reflex_trigger.png](images/reflex_trigger.png) |
| **C** | Lineage for one sample | [images/lineage.png](images/lineage.png) |
| **D** | Exception detection (missing reflex) | [images/exception_detection.png](images/exception_detection.png) |
| **E** | Final status (derived) | [images/final_status.png](images/final_status.png) |
