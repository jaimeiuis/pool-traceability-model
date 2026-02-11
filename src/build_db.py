import sqlite3
import random
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

random.seed(7)

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "pool_traceability.db"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"

def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")

def main():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    # Apply schema
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    # Parameters
    n_samples = 120
    pool_size = 4
    n_pools = n_samples // pool_size

    base_time = datetime(2026, 2, 1, 8, 0, 0)
    sites = ["SITE_A", "SITE_B", "SITE_C"]

    # Samples
    samples = []
    for i in range(1, n_samples + 1):
        sample_id = f"SAMPLE_{i:04d}"
        patient_id = f"PT_{(i%80)+1:03d}"
        site_id = random.choice(sites)
        collected_at = base_time + timedelta(minutes=random.randint(0, 600))
        samples.append((sample_id, patient_id, site_id, iso(collected_at)))

    conn.executemany(
        "INSERT INTO samples(sample_id, patient_id, site_id, collected_at) VALUES (?,?,?,?)",
        samples
    )

    # Pools + members
    pools = []
    pool_members = []
    sample_ids = [s[0] for s in samples]
    random.shuffle(sample_ids)

    for p in range(1, n_pools + 1):
        pool_id = f"POOL_{p:04d}"
        created_at = base_time + timedelta(hours=1, minutes=p)
        pools.append((pool_id, iso(created_at), "optimistic", None))

        members = sample_ids[(p-1)*pool_size : p*pool_size]
        for sid in members:
            pool_members.append((pool_id, sid))

    conn.executemany(
        "INSERT INTO pools(pool_id, created_at, pool_strategy, notes) VALUES (?,?,?,?)",
        pools
    )
    conn.executemany(
        "INSERT INTO pool_members(pool_id, sample_id) VALUES (?,?)",
        pool_members
    )

    # Pool tests: mostly NEG; some BORDERLINE/POS to trigger reflex
    tests = []
    run_counter = 1

    # choose pools to be borderline/positive
    borderline_pools = set(random.sample([p[0] for p in pools], k=max(3, n_pools//10)))
    positive_pools = set(random.sample([p for p in [pp[0] for pp in pools] if p not in borderline_pools],
                                       k=max(2, n_pools//20)))

    for pool_id, created_at, _, _ in pools:
        run_id = f"RUN_{run_counter:03d}"
        run_counter += 1
        tested_at = datetime.fromisoformat(created_at) + timedelta(hours=2)

        if pool_id in positive_pools:
            result = "POS"
            ct = round(random.uniform(18.0, 28.0), 1)
            reflex = 1
        elif pool_id in borderline_pools:
            result = "BORDERLINE"
            ct = round(random.uniform(30.0, 37.5), 1)
            reflex = 1
        else:
            result = "NEG"
            ct = None
            reflex = 0

        tests.append((f"T_POOL_{pool_id}", "POOL", pool_id, run_id, result, ct, iso(tested_at), reflex))

    conn.executemany(
        "INSERT INTO tests(test_id, entity_type, entity_id, run_id, result, ct_value, tested_at, reflex_triggered) "
        "VALUES (?,?,?,?,?,?,?,?)",
        tests
    )

    # Reflex tests on samples in borderline/positive pools
    # For POS pools, make exactly one member POS; others NEG.
    # For BORDERLINE pools, make one member BORDERLINE; rest NEG.
    # Also leave a couple missing reflex tests to create "exceptions".
    exceptions_to_create = 3  # number of missing reflex tests
    skipped = 0

    # Map pool -> members
    pool_to_members = {}
    for pool_id, sid in pool_members:
        pool_to_members.setdefault(pool_id, []).append(sid)

    reflex_tests = []
    for pool_id in (borderline_pools | positive_pools):
        members = pool_to_members[pool_id]
        trigger_sample = random.choice(members)

        for sid in members:
            # Create some missing reflex tests as intentional exceptions
            if skipped < exceptions_to_create and random.random() < 0.10:
                skipped += 1
                continue

            run_id = f"RUN_{run_counter:03d}"
            run_counter += 1
            tested_at = base_time + timedelta(days=1, minutes=random.randint(0, 600))

            if sid == trigger_sample:
                if pool_id in positive_pools:
                    result = "POS"
                    ct = round(random.uniform(20.0, 30.0), 1)
                else:
                    result = "BORDERLINE"
                    ct = round(random.uniform(32.0, 38.5), 1)
            else:
                result = "NEG"
                ct = None

            reflex_tests.append((f"T_S_{sid}", "SAMPLE", sid, run_id, result, ct, iso(tested_at), 0))

    conn.executemany(
        "INSERT INTO tests(test_id, entity_type, entity_id, run_id, result, ct_value, tested_at, reflex_triggered) "
        "VALUES (?,?,?,?,?,?,?,?)",
        reflex_tests
    )

    conn.commit()

    # Quick sanity summary for you
    df = pd.read_sql_query(
        "SELECT entity_type, result, COUNT(*) AS n FROM tests GROUP BY entity_type, result ORDER BY entity_type, result",
        conn
    )
    print("Created:", DB_PATH)
    print(df.to_string(index=False))

    conn.close()

if __name__ == "__main__":
    main()
