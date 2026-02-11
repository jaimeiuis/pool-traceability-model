# Query results (for screenshots)

Run: `python src/run_queries.py` to regenerate. Below is the output from the last run.

---

## A) Pool membership

**Query:** Members of `POOL_0001`, ordered by sample_id.

| pool_id   | sample_id  |
|-----------|------------|
| POOL_0001 | SAMPLE_0003 |
| POOL_0001 | SAMPLE_0013 |
| POOL_0001 | SAMPLE_0015 |
| POOL_0001 | SAMPLE_0108 |

*(4 rows)*

---

## B) Pools that triggered reflex testing

**Query:** Pool tests with result BORDERLINE or POS.

| pool_id   | result    | ct_value | tested_at          |
|-----------|------------|----------|---------------------|
| POOL_0006 | POS        | 18.0     | 2026-02-01T11:06:00 |
| POOL_0015 | BORDERLINE | 36.0     | 2026-02-01T11:15:00 |
| POOL_0021 | POS        | 19.7     | 2026-02-01T11:21:00 |
| POOL_0025 | BORDERLINE | 33.6     | 2026-02-01T11:25:00 |
| POOL_0028 | BORDERLINE | 35.4     | 2026-02-01T11:28:00 |

*(5 rows)*

---

## C) Lineage for one sample (SAMPLE_0042)

**Query:** Pool → pool test → reflex test for sample SAMPLE_0042.

| sample_id   | pool_id   | pool_result | pool_ct | reflex_result | reflex_ct |
|-------------|-----------|-------------|---------|---------------|-----------|
| SAMPLE_0042 | POOL_0012 | NEG         | *null*  | *null*        | *null*    |

*(1 row)*  
*(Pool is NEG so no reflex test.)*

---

## D) Exception detection (missing reflex)

**Query:** Pools that required reflex but have at least one member with no reflex test.

| pool_id   | sample_id  |
|-----------|------------|
| POOL_0025 | SAMPLE_0046 |
| POOL_0028 | SAMPLE_0098 |

*(2 rows)*

---

## E) Final status (derived)

**Query:** All samples with derived final_status (FINAL_NEG, FINAL_POS_REVIEW, PENDING_REFLEX).

*Summary:* 120 rows total.

- **FINAL_NEG:** Pool NEG, or pool POS/BORDERLINE and reflex NEG (e.g. SAMPLE_0003…SAMPLE_0113, plus reflex-NEG members of POS/BORDERLINE pools).
- **FINAL_POS_REVIEW:** Pool POS or BORDERLINE and reflex POS or BORDERLINE (5 rows: SAMPLE_0017, SAMPLE_0060, SAMPLE_0102, SAMPLE_0094, SAMPLE_0110).
- **PENDING_REFLEX:** Pool POS or BORDERLINE but no reflex test (2 rows: SAMPLE_0046, SAMPLE_0098 — matches query D).

*(Full 120-row result set available by running `python src/run_queries.py`.)*
