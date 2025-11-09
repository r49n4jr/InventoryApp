import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.database_manager import DatabaseManager
from models.items_repository import ItemsRepository


def main():
    db_path = ROOT / 'db' / 'tmp_items.db'
    db = DatabaseManager(str(db_path))
    db.initialize()
    repo = ItemsRepository(db)

    # Insert sample items
    a_id = repo.insert(name='Screw M4', unit='pcs', code='SCREW-M4', barcode='123456', current_stock=100)
    b_id = repo.insert(name='Nut M4', unit='pcs', code='NUT-M4', barcode='234567', current_stock=50)

    # Search by name
    by_name = repo.search('Screw')
    # Search by code
    by_code = repo.search('NUT-')
    # Search by barcode
    by_barcode = repo.search('234567')

    # Update stock
    repo.update_stock(a_id, 90)

    # Fetch after update
    item_a = repo.get_by_id(a_id)

    print('by_name', [r['name'] for r in by_name])
    print('by_code', [r['code'] for r in by_code])
    print('by_barcode', [r['barcode'] for r in by_barcode])
    print('item_a_stock', item_a['current_stock'])


if __name__ == '__main__':
    main()
