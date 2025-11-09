from __future__ import annotations
import sqlite3
from typing import Optional, List, Dict, Any

from .database_manager import DatabaseManager


def _row_to_dict(cursor: sqlite3.Cursor, row: tuple) -> Dict[str, Any]:
    cols = [d[0] for d in cursor.description]
    return {k: v for k, v in zip(cols, row)}


class ItemsRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        with self.db.connect() as conn:
            cur = conn.execute(
                "SELECT id, code, name, group_id, unit, barcode, current_stock, active, created_at, updated_at FROM items WHERE id=?",
                (item_id,),
            )
            row = cur.fetchone()
            return _row_to_dict(cur, row) if row else None

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        with self.db.connect() as conn:
            cur = conn.execute(
                "SELECT id, code, name, group_id, unit, barcode, current_stock, active, created_at, updated_at FROM items WHERE name=?",
                (name,),
            )
            row = cur.fetchone()
            return _row_to_dict(cur, row) if row else None

    def search(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        like = f"%{keyword}%"
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                SELECT id, code, name, group_id, unit, barcode, current_stock, active
                FROM items
                WHERE name LIKE ? OR code LIKE ? OR barcode LIKE ?
                ORDER BY name ASC
                LIMIT ?
                """,
                (like, like, like, limit),
            )
            rows = cur.fetchall()
            return [_row_to_dict(cur, r) for r in rows]

    def insert(
        self,
        *,
        name: str,
        unit: str = "pcs",
        code: Optional[str] = None,
        barcode: Optional[str] = None,
        current_stock: int = 0,
        group_id: Optional[int] = None,
        active: int = 1,
    ) -> int:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO items (code, name, group_id, unit, barcode, current_stock, active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (code, name, group_id, unit, barcode, current_stock, active),
            )
            return int(cur.lastrowid)

    def update(
        self,
        item_id: int,
        *,
        name: Optional[str] = None,
        unit: Optional[str] = None,
        code: Optional[str] = None,
        barcode: Optional[str] = None,
        current_stock: Optional[int] = None,
        group_id: Optional[int] = None,
        active: Optional[int] = None,
    ) -> None:
        fields = []
        params: List[Any] = []
        if code is not None:
            fields.append("code=?"); params.append(code)
        if name is not None:
            fields.append("name=?"); params.append(name)
        if group_id is not None:
            fields.append("group_id=?"); params.append(group_id)
        if unit is not None:
            fields.append("unit=?"); params.append(unit)
        if barcode is not None:
            fields.append("barcode=?"); params.append(barcode)
        if current_stock is not None:
            fields.append("current_stock=?"); params.append(current_stock)
        if active is not None:
            fields.append("active=?"); params.append(active)
        if not fields:
            return
        params.append(item_id)
        sql = f"UPDATE items SET {', '.join(fields)}, updated_at=datetime('now') WHERE id=?"
        with self.db.connect() as conn:
            conn.execute(sql, tuple(params))

    def set_active(self, item_id: int, active: int) -> None:
        with self.db.connect() as conn:
            conn.execute(
                "UPDATE items SET active=?, updated_at=datetime('now') WHERE id=?",
                (active, item_id),
            )

    def update_stock(self, item_id: int, new_stock: int) -> None:
        with self.db.connect() as conn:
            conn.execute(
                "UPDATE items SET current_stock=?, updated_at=datetime('now') WHERE id=?",
                (new_stock, item_id),
            )
