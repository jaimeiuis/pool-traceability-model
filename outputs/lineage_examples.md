# Lineage examples

Generated after running `python src/build_db.py --seed` and querying the DB.

## Seed setup

- **Pool-A**: samples S001, S002, S003. Pool test: **positive**.
- **Pool-B**: samples S004, S005. Pool test: **negative**.
- Reflex: S001 → positive, S002 → negative; **S003 has no reflex** (exception).

---

## `SELECT * FROM sample_lineage`

| sample_id | sample_external_id | pool_id | pool_name | pool_test_result | reflex_test_result | final_result    |
|-----------|--------------------|---------|-----------|------------------|--------------------|-----------------|
| 1         | S001               | 1       | Pool-A    | positive         | positive           | positive        |
| 2         | S002               | 1       | Pool-A    | positive         | negative           | negative        |
| 3         | S003               | 1       | Pool-A    | positive         | *NULL*             | pending_reflex  |
| 4         | S004               | 2       | Pool-B    | negative         | *NULL*             | negative        |
| 5         | S005               | 2       | Pool-B    | negative         | *NULL*             | negative        |

Interpretation: for each sample, lineage is **pool test → reflex test (if any) → final**. S003 is the exception (pool positive, reflex missing).

---

## `SELECT * FROM reflex_exceptions`

| sample_id | sample_external_id | pool_id | pool_name | pool_test_result | reflex_test_id | reflex_test_result | exception_type            |
|-----------|--------------------|---------|-----------|------------------|----------------|--------------------|---------------------------|
| 3         | S003               | 1       | Pool-A    | positive         | NULL           | NULL               | reflex_missing_or_pending  |

Only samples that require a reflex (pool positive/borderline) but have no reflex or pending reflex appear here.

---

## Final reporting derivation (reference)

| Pool result   | Reflex status        | Final result   |
|---------------|----------------------|----------------|
| negative      | (any)                | **negative**   |
| positive      | positive/negative/indeterminate | **reflex result** |
| positive      | missing or pending   | **pending_reflex** |
| borderline    | positive/negative/indeterminate | **reflex result** |
| borderline    | missing or pending   | **pending_reflex** |
