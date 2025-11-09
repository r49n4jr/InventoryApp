import sys
import sqlite3
from pathlib import Path
import json

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.database_manager import initialize_database

db_path = ROOT / 'db' / 'tmp_schema.db'
initialize_database(str(db_path))

conn = sqlite3.connect(str(db_path))
try:
    cur = conn.execute(
        "SELECT type, name, tbl_name FROM sqlite_master WHERE type IN ('table','index') ORDER BY type, name"
    )
    rows = cur.fetchall()
    print(json.dumps(rows, indent=2))
finally:
    conn.close()
