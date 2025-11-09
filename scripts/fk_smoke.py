import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.database_manager import DatabaseManager


def main():
    db_path = ROOT / 'db' / 'tmp_fk.db'
    db = DatabaseManager(str(db_path))
    db.initialize()

    with db.transaction() as conn:
        # Insert an item
        cur = conn.execute("INSERT INTO items (name, unit) VALUES (?, ?)", ("Widget", "pcs"))
        item_id = cur.lastrowid
        # Insert a transaction
        cur = conn.execute(
            "INSERT INTO transactions (transaction_number, person_name, transaction_type) VALUES (?,?,?)",
            ("TRX-001", "John", "OUT"),
        )
        trx_id = cur.lastrowid
        # Insert a transaction_item referencing both
        conn.execute(
            "INSERT INTO transaction_items (transaction_id, item_id, quantity, stock_before, stock_after) VALUES (?,?,?,?,?)",
            (trx_id, item_id, 2, 10, 8),
        )

    # Now delete the transaction and verify cascade deletes transaction_items
    with db.transaction() as conn:
        conn.execute("DELETE FROM transactions WHERE id=?", (trx_id,))

    with db.connect() as conn:
        cnt = conn.execute("SELECT COUNT(*) FROM transaction_items WHERE transaction_id=?", (trx_id,)).fetchone()[0]
        print("remaining_trx_items", cnt)


if __name__ == '__main__':
    main()
