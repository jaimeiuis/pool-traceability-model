Problem: Some lab workflows require pooled testing with reflex retesting, but systems may not natively support parent/child traceability (pool ↔ constituent samples) and exception routing.

Solution: This project demonstrates a minimal, queryable traceability model in SQLite:

- Pools and membership

- Pool-level test results

- Reflex tests for constituent samples

- Lineage queries and exception detection (missing reflex)

Key outputs: lineage query, exception report query, and derived final reporting status.

## Images

Query result screenshots (see [images/](images/)):

| Query | Description | Screenshot |
|-------|--------------|------------|
| **A** | Pool membership | [images/pool_membership.png](images/pool_membership.png) |
| **B** | Pools that triggered reflex testing | [images/reflex_trigger.png](images/reflex_trigger.png) |
| **C** | Lineage for one sample | [images/lineage.png](images/lineage.png) |
| **D** | Exception detection (missing reflex) | [images/exception_detection.png](images/exception_detection.png) |
| **E** | Final status (derived) | [images/final_status.png](images/final_status.png) |
