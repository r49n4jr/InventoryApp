import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

# Ensure project root on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.manager import ConfigManager
from models.database_manager import DatabaseManager


def backup_csv(csv_path: Path, backup_path: Path) -> None:
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(csv_path, backup_path)


def read_csv(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # Normalize columns expected: Item, Stock, Unit
    cols = {c.lower(): c for c in df.columns}
    # Coerce to standard names if case differs
    def col_get(name: str) -> str:
        return cols.get(name.lower(), name)
    # Trim and fill
    if col_get('Item') not in df.columns:
        raise ValueError("CSV missing required column 'Item'")
    item_col = col_get('Item')
    stock_col = col_get('Stock') if col_get('Stock') in df.columns else None
    unit_col = col_get('Unit') if col_get('Unit') in df.columns else None

    out = pd.DataFrame()
    out['name'] = df[item_col].astype(str).str.strip()
    if stock_col:
        out['current_stock'] = pd.to_numeric(df[stock_col], errors='coerce').fillna(0).astype(int)
    else:
        out['current_stock'] = 0
    if unit_col:
        out['unit'] = df[unit_col].astype(str).str.strip().replace({'': 'pcs'})
    else:
        out['unit'] = 'pcs'
    return out


def transform(df: pd.DataFrame) -> (pd.DataFrame, List[Dict[str, Any]]):
    # Drop rows with empty name
    df = df[df['name'].astype(str).str.len() > 0].copy()
    # Keep first occurrence by name; mark duplicates
    duplicates_report: List[Dict[str, Any]] = []
    duplicated_mask = df.duplicated(subset=['name'], keep='first')
    if duplicated_mask.any():
        dup_rows = df[duplicated_mask]
        for _, r in dup_rows.iterrows():
            duplicates_report.append({'name': r['name']})
        df = df[~duplicated_mask]
    # Ensure defaults
    if 'unit' not in df.columns:
        df['unit'] = 'pcs'
    if 'current_stock' not in df.columns:
        df['current_stock'] = 0
    return df, duplicates_report


def load_to_db(db: DatabaseManager, df: pd.DataFrame, dry_run: bool = False, batch_size: int = 200) -> Dict[str, Any]:
    inserted = 0
    skipped = 0
    conflicts: List[Dict[str, Any]] = []
    rows = df.to_dict(orient='records')
    if dry_run:
        return {"inserted": 0, "skipped": 0, "conflicts": []}

    # Batch inserts
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        with db.transaction() as conn:
            for r in batch:
                try:
                    conn.execute(
                        "INSERT INTO items (name, unit, current_stock, active) VALUES (?,?,?,1)",
                        (r['name'], r['unit'], int(r['current_stock'])),
                    )
                    inserted += 1
                except Exception as ex:
                    skipped += 1
                    conflicts.append({"name": r['name'], "error": str(ex)})
    return {"inserted": inserted, "skipped": skipped, "conflicts": conflicts}


def spot_check(db: DatabaseManager, names: List[str]) -> List[Dict[str, Any]]:
    out = []
    with db.connect() as conn:
        for name in names:
            row = conn.execute(
                "SELECT name, unit, current_stock FROM items WHERE name=?",
                (name,),
            ).fetchone()
            if row:
                out.append({"name": row[0], "unit": row[1], "current_stock": row[2]})
    return out


def write_report(report_path: Path, report: Dict[str, Any]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description="Migrate CSV items to SQLite")
    parser.add_argument('--csv', dest='csv_path', default=None, help='Path to source CSV (default: from config)')
    parser.add_argument('--db', dest='db_path', default=None, help='Path to SQLite DB (default: from config)')
    parser.add_argument('--dry-run', action='store_true', help='Run without writing to DB')
    parser.add_argument('--batch-size', type=int, default=200, help='Insert batch size')
    args = parser.parse_args()

    cfg = ConfigManager()
    csv_path = Path(args.csv_path or (ROOT / cfg.csv_path))
    db_path = Path(args.db_path or (ROOT / cfg.db_path))

    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        sys.exit(1)

    # Backup
    backup_path = csv_path.parent / (csv_path.stem + '.backup.csv')
    try:
        if not args.dry_run:
            backup_csv(csv_path, backup_path)
    except Exception as e:
        print(f"Backup failed: {e}")
        sys.exit(1)

    # Read & transform
    try:
        src_df = read_csv(csv_path)
        norm_df, duplicates = transform(src_df)
    except Exception as e:
        print(f"Read/transform failed: {e}")
        sys.exit(1)

    # Initialize DB
    db = DatabaseManager(str(db_path))
    db.initialize()

    # Load
    load_summary = load_to_db(db, norm_df, dry_run=args.dry_run, batch_size=args.batch_size)

    # Verify
    sample_names = list(norm_df['name'].head(5))
    checks = spot_check(db, sample_names) if not args.dry_run else []

    # Report
    report = {
        "csv": str(csv_path),
        "db": str(db_path),
        "dry_run": args.dry_run,
        "total_source_rows": int(len(src_df)),
        "total_after_transform": int(len(norm_df)),
        "duplicates_by_name": duplicates,
        "load": load_summary,
        "spot_checks": checks,
    }
    report_path = ROOT / 'logs' / 'migration_report.json'
    write_report(report_path, report)
    print(json.dumps({
        "inserted": load_summary["inserted"],
        "skipped": load_summary["skipped"],
        "duplicates": len(duplicates),
        "report": str(report_path)
    }, indent=2))


if __name__ == '__main__':
    main()
