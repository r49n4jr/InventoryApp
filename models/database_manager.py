import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, Optional

from config.manager import ConfigManager


DDL_STATEMENTS = [
    # product_groups
    """
    CREATE TABLE IF NOT EXISTS product_groups (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        parent_id INTEGER REFERENCES product_groups(id),
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,
    # items (barcode NOT UNIQUE per user), code UNIQUE
    """
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        code TEXT UNIQUE,
        name TEXT NOT NULL,
        group_id INTEGER REFERENCES product_groups(id),
        unit TEXT NOT NULL DEFAULT 'pcs',
        barcode TEXT UNIQUE,
        current_stock INTEGER NOT NULL DEFAULT 0,
        active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,
    # indexes
    """CREATE INDEX IF NOT EXISTS idx_items_name ON items(name);""",
    """CREATE INDEX IF NOT EXISTS idx_items_code ON items(code);""",
    """CREATE INDEX IF NOT EXISTS idx_items_barcode ON items(barcode);""",
    # transactions
    """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        transaction_number TEXT UNIQUE NOT NULL,
        person_name TEXT NOT NULL,
        transaction_type TEXT NOT NULL CHECK (transaction_type IN ('OUT','IN','ADJUST')),
        notes TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,
    # transaction_items
    """
    CREATE TABLE IF NOT EXISTS transaction_items (
        id INTEGER PRIMARY KEY,
        transaction_id INTEGER NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
        item_id INTEGER NOT NULL REFERENCES items(id),
        quantity INTEGER NOT NULL,
        stock_before INTEGER NOT NULL,
        stock_after INTEGER NOT NULL
    );
    """,
    # index for transaction_items
    """CREATE INDEX IF NOT EXISTS idx_trx_items_trx ON transaction_items(transaction_id);""",
    # stock_adjustments
    """
    CREATE TABLE IF NOT EXISTS stock_adjustments (
        id INTEGER PRIMARY KEY,
        item_id INTEGER NOT NULL REFERENCES items(id),
        old_stock INTEGER NOT NULL,
        new_stock INTEGER NOT NULL,
        adjustment INTEGER NOT NULL,
        reason TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,
]


class DatabaseManager:
    """Lightweight SQLite manager with schema initialization.

    Not wired into the app yet; safe to import and call `initialize()` to create schema.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            cfg = ConfigManager()
            db_path = cfg.db_path
        self.db_path = Path(db_path)
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(str(self.db_path))
        try:
            # Foreign keys enforcement
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn
            conn.commit()
        finally:
            conn.close()

    def execute(self, sql: str, params: Iterable[Any] | None = None) -> None:
        with self.connect() as conn:
            conn.execute(sql, tuple(params or ()))

    def executemany(self, sql: str, seq_of_params: Iterable[Iterable[Any]]) -> None:
        with self.connect() as conn:
            conn.executemany(sql, seq_of_params)

    def query_one(self, sql: str, params: Iterable[Any] | None = None) -> Optional[tuple]:
        with self.connect() as conn:
            cur = conn.execute(sql, tuple(params or ()))
            return cur.fetchone()

    def query_all(self, sql: str, params: Iterable[Any] | None = None) -> list[tuple]:
        with self.connect() as conn:
            cur = conn.execute(sql, tuple(params or ()))
            return cur.fetchall()

    def initialize(self) -> None:
        """Create tables and indexes if they don't exist."""
        with self.connect() as conn:
            for stmt in DDL_STATEMENTS:
                conn.executescript(stmt)

    @contextmanager
    def transaction(self):
        """Context manager for an explicit transaction.

        Usage:
            with db.transaction() as conn:
                conn.execute(...)
        """
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("BEGIN;")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


def initialize_database(db_path: Optional[str] = None) -> Path:
    manager = DatabaseManager(db_path)
    manager.initialize()
    return manager.db_path
