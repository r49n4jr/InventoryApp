# Database Notes: CSV → SQLite Mapping and Decisions

## Mapping
- CSV `Item` → `items.name`
- CSV `Stock` → `items.current_stock` (non-integer coerced to 0)
- CSV `Unit` → `items.unit` (defaults to `pcs` if missing)

## Constraints & Rules
- `items.code` is UNIQUE (nullable)
- `items.barcode` is UNIQUE (nullable)
- `transactions.transaction_type` ∈ {OUT, IN, ADJUST}
- Timestamps default to `datetime('now')` (UTC) in SQLite
- Foreign keys enabled (`PRAGMA foreign_keys=ON`)
- `transaction_items.transaction_id` → `transactions.id` has `ON DELETE CASCADE`

## Duplicates Policy (CSV → DB)
- Duplicates by `name`: keep the first occurrence, skip subsequent; log skipped rows in migration report.

## Indexes
- `items(name)`, `items(code)`, `items(barcode)`
- `transaction_items(transaction_id)`
- `product_groups(parent_id)` (implicit via hierarchy queries later)

## Notes
- Existing DBs created before constraint changes may require migrations to enforce new rules.
- Future phases will add more constraints/indices as needed for performance.
