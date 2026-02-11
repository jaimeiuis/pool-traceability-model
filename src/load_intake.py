"""
Load the upstream clean intake contract (clean_intake.csv) into the SQLite traceability model.

- Ensures schema exists (runs sql/schema.sql)
- Loads samples from clean_intake.csv into samples table
- Optionally loads pool_plan.csv into pools and pool_members
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "pool_traceability.db"
DEFAULT_SCHEMA = ROOT / "sql" / "schema.sql"


def ensure_schema(conn: sqlite3.Connection, schema_path: Path) -> None:
    conn.execute("PRAGMA foreign_keys = ON;")
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())


def load_clean_intake(conn: sqlite3.Connection, clean_intake_csv: Path) -> int:
    """
    Expects Project #1 contract columns (extra columns are ignored):
      barcode, patient_id, site_id, collected_at, scanned_at, source, batch_id, operator_id
    """
    df = pd.read_csv(clean_intake_csv, dtype=str).fillna("")

    # Basic validation
    if "barcode" not in df.columns:
        raise ValueError("clean_intake.csv must contain a 'barcode' column.")

    rows = []
    for _, r in df.iterrows():
        sample_id = str(r.get("barcode", "")).strip()
        if not sample_id:
            continue

        patient_id = str(r.get("patient_id", "")).strip() or "PT_UNKNOWN"
        site_id = str(r.get("site_id", "")).strip() or "SITE_UNKNOWN"

        # Prefer collected_at; else fallback to scanned_at; else generate a timestamp
        collected_at = str(r.get("collected_at", "")).strip()
        scanned_at = str(r.get("scanned_at", "")).strip()
        collected = collected_at or scanned_at
        if not collected:
            collected = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        rows.append((sample_id, patient_id, site_id, collected))

    conn.executemany(
        "INSERT OR IGNORE INTO samples(sample_id, patient_id, site_id, collected_at) VALUES (?,?,?,?)",
        rows,
    )
    return len(rows)


def load_pool_plan(conn: sqlite3.Connection, pool_plan_csv: Path) -> dict:
    """
    Optional. Expects columns:
      pool_id, sample_id, created_at, pool_strategy
    """
    df = pd.read_csv(pool_plan_csv, dtype=str).fillna("")

    required = {"pool_id", "sample_id"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"pool_plan.csv missing required columns: {sorted(missing)}")

    # Insert pools (unique)
    pools = df[["pool_id", "created_at", "pool_strategy"]].copy()
    if "created_at" not in pools.columns:
        pools["created_at"] = ""
    if "pool_strategy" not in pools.columns:
        pools["pool_strategy"] = ""

    pools = pools.drop_duplicates()

    pool_rows = []
    for _, p in pools.iterrows():
        pool_id = str(p.get("pool_id", "")).strip()
        if not pool_id:
            continue

        created_at = str(p.get("created_at", "")).strip()
        if not created_at:
            created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        strategy = str(p.get("pool_strategy", "")).strip() or "optimistic"
        pool_rows.append((pool_id, created_at, strategy, None))

    conn.executemany(
        "INSERT OR IGNORE INTO pools(pool_id, created_at, pool_strategy, notes) VALUES (?,?,?,?)",
        pool_rows,
    )

    # Insert membership
    mem_rows = []
    for _, r in df.iterrows():
        pool_id = str(r.get("pool_id", "")).strip()
        sample_id = str(r.get("sample_id", "")).strip()
        if pool_id and sample_id:
            mem_rows.append((pool_id, sample_id))

    conn.executemany(
        "INSERT OR IGNORE INTO pool_members(pool_id, sample_id) VALUES (?,?)",
        mem_rows,
    )

    return {"pools_inserted": len(pool_rows), "memberships_inserted": len(mem_rows)}


def main(clean_intake: str, pool_plan: str = "", db: str = "", schema: str = "") -> None:
    clean_intake_path = Path(clean_intake)
    if not clean_intake_path.exists():
        raise FileNotFoundError(f"clean_intake.csv not found: {clean_intake_path}")

    db_path = Path(db) if db else DEFAULT_DB
    schema_path = Path(schema) if schema else DEFAULT_SCHEMA

    conn = sqlite3.connect(db_path)
    ensure_schema(conn, schema_path)

    n_samples = load_clean_intake(conn, clean_intake_path)

    pool_stats = None
    if pool_plan:
        pool_plan_path = Path(pool_plan)
        if not pool_plan_path.exists():
            raise FileNotFoundError(f"pool_plan.csv not found: {pool_plan_path}")
        pool_stats = load_pool_plan(conn, pool_plan_path)

    conn.commit()
    conn.close()

    print(f"DB: {db_path}")
    print(f"Loaded samples: {n_samples} (attempted inserts via INSERT OR IGNORE)")
    if pool_stats:
        print(f"Loaded pool plan: {pool_stats}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Load clean_intake.csv (Project #1 contract) into the pooling traceability SQLite DB."
    )
    parser.add_argument("--clean-intake", required=True, help="Path to outputs/clean_intake.csv from Project #1")
    parser.add_argument("--pool-plan", required=False, default="", help="Optional path to pool_plan.csv")
    parser.add_argument("--db", required=False, default="", help="SQLite DB path (default: pool_traceability.db)")
    parser.add_argument("--schema", required=False, default="", help="Schema SQL path (default: sql/schema.sql)")
    args = parser.parse_args()

    main(clean_intake=args.clean_intake, pool_plan=args.pool_plan, db=args.db, schema=args.schema)
