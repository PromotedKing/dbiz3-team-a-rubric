"""Build the SQLite database from the schema and the seed (specs/001-alr-core/research.md R2).

data/ is read-only: the schema and the CSV files are executed / loaded as they are,
in filename order, which is foreign-key order (data/data-model-MB360.md §10)."""
import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "data" / "schema" / "schema-MB360.sql"
SEED_DIR = ROOT / "data" / "seed"


def build(path: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    conn.execute("PRAGMA foreign_keys = ON")
    for csv_path in sorted(SEED_DIR.glob("[0-9][0-9]_*.csv")):
        table = csv_path.stem.split("_", 1)[1]
        with csv_path.open(encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = [[None if cell == "" else cell for cell in row] for row in reader]
        cols = ", ".join(header)
        marks = ", ".join("?" for _ in header)
        conn.executemany(f"INSERT INTO {table} ({cols}) VALUES ({marks})", rows)
    conn.commit()
    return conn
