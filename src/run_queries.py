"""Run the five queries from sql/queries.sql and print results."""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "pool_traceability.db"

QUERY_A = """
SELECT pm.pool_id, pm.sample_id
FROM pool_members pm
WHERE pm.pool_id = 'POOL_0001'
ORDER BY pm.sample_id;
"""

QUERY_B = """
SELECT entity_id AS pool_id, result, ct_value, tested_at
FROM tests
WHERE entity_type='POOL' AND result IN ('BORDERLINE','POS')
ORDER BY tested_at;
"""

QUERY_C = """
SELECT s.sample_id, pm.pool_id, pt.result AS pool_result, pt.ct_value AS pool_ct,
       rt.result AS reflex_result, rt.ct_value AS reflex_ct
FROM samples s
JOIN pool_members pm ON pm.sample_id = s.sample_id
LEFT JOIN tests pt ON pt.entity_type='POOL' AND pt.entity_id = pm.pool_id
LEFT JOIN tests rt ON rt.entity_type='SAMPLE' AND rt.entity_id = s.sample_id
WHERE s.sample_id = 'SAMPLE_0042';
"""

QUERY_D = """
SELECT pm.pool_id, pm.sample_id
FROM pool_members pm
JOIN tests pt ON pt.entity_type='POOL' AND pt.entity_id = pm.pool_id
LEFT JOIN tests rt ON rt.entity_type='SAMPLE' AND rt.entity_id = pm.sample_id
WHERE pt.result IN ('BORDERLINE','POS') AND rt.test_id IS NULL
ORDER BY pm.pool_id, pm.sample_id;
"""

QUERY_E = """
SELECT s.sample_id, pm.pool_id, pt.result AS pool_result, rt.result AS reflex_result,
       CASE
         WHEN pt.result = 'NEG' THEN 'FINAL_NEG'
         WHEN rt.result IN ('POS','BORDERLINE') THEN 'FINAL_POS_REVIEW'
         WHEN rt.result = 'NEG' THEN 'FINAL_NEG'
         ELSE 'PENDING_REFLEX'
       END AS final_status
FROM samples s
JOIN pool_members pm ON pm.sample_id = s.sample_id
JOIN tests pt ON pt.entity_type='POOL' AND pt.entity_id = pm.pool_id
LEFT JOIN tests rt ON rt.entity_type='SAMPLE' AND rt.entity_id = pm.sample_id
ORDER BY final_status, pm.pool_id, s.sample_id;
"""


def run(title: str, sql: str, conn: sqlite3.Connection) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    if not rows:
        print("(no rows)")
        return
    names = [d[0] for d in cur.description]
    print(" | ".join(names))
    print("-" * 60)
    for r in rows:
        print(" | ".join(str(v) for v in r))
    print(f"({len(rows)} row(s))")


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    run("A) Pool membership", QUERY_A, conn)
    run("B) Pools that triggered reflex testing", QUERY_B, conn)
    run("C) Lineage for one sample (SAMPLE_0042)", QUERY_C, conn)
    run("D) Exception detection (missing reflex)", QUERY_D, conn)
    run("E) Final status (derived)", QUERY_E, conn)
    conn.close()


if __name__ == "__main__":
    main()
