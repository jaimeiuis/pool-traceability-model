"""
Export pool_traceability.db to a readable Markdown file (outputs/db_export.md).
Run after build_db.py to inspect data in the editor.
"""
import sqlite3
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "pool_traceability.db"
OUT_PATH = ROOT / "outputs" / "db_export.md"


def main() -> None:
    if not DB_PATH.exists():
        print(f"No database at {DB_PATH}. Run build_db.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    tables = ["samples", "pools", "pool_members", "tests"]
    parts = ["# Database export: pool_traceability.db\n"]

    for table in tables:
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        except sqlite3.OperationalError:
            parts.append(f"## {table}\n*(table missing or empty)*\n")
            continue
        parts.append(f"## {table}\n\n")
        parts.append("```\n")
        parts.append(df.to_string(index=False))
        parts.append("\n```\n\n")

    conn.close()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("".join(parts), encoding="utf-8")
    print(f"Exported to {OUT_PATH}")


if __name__ == "__main__":
    main()
