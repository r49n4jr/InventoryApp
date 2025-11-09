# Inventory Management System - Development Roadmap

## Project Overview
Transform the current simple POS system into a comprehensive inventory tracking system similar to Aronium, focused on stock management rather than sales. The system will track item movements (in/out), maintain transaction history, and provide detailed reporting capabilities.

## Core Principles
- **Stock-based, not sales-based**: No pricing, revenue, or payment tracking
- **Transaction history**: Every stock movement is recorded with person name and timestamp
- **Multi-section interface**: Tabbed navigation for different functions
- **Database-driven**: SQLite for portability and reliability
- **Weekly development pace**: Build incrementally while keeping current system working

---

## Phase 1: Foundation & Code Refactoring --PHASE 1DONE--
**Goal**: Clean up existing code, improve structure, and prepare for expansion

### 1.1 Project Structure Reorganization --DONE--
- [v] Create proper folder structure:
  ```
  /models          # Database models and business logic
  /ui              # UI components and windows
  /utils           # Helper functions and utilities
  /config          # Configuration management
  /reports         # Report generation logic
  /data            # Database and data files
  ```
- [v] Move existing code into appropriate folders
- [v] Update imports across all files

### 1.2 Configuration System --DONE--
- [v] Create `config.json` for application settings
- [v] Add configurable settings:
  - Printer port (currently hardcoded as COM6)
  - Database path
  - Application name/company info
  - Default units
- [v] Create `ConfigManager` class to load/save settings
- [v] Update code to use config instead of hardcoded values

### 1.3 Error Handling & Logging --DONE--
- [v] Add proper try-except blocks throughout code
- [v] Implement logging system (file-based logs)
- [v] Add user-friendly error messages
- [v] Create error recovery mechanisms (especially for printer failures)

### 1.4 Code Quality Improvements --DONE--
- [v] Add docstrings to all classes and methods
- [v] Implement input validation
- [v] Remove duplicate code
- [v] Add constants file for magic numbers/strings

**Deliverable**: Cleaner, more maintainable codebase with configuration support --PHASE 1DONE--

---

## Phase 2: Database Migration
**Goal**: Replace CSV with SQLite database for better data management

### 2.1 Database Schema Design --IN PROGRESS--
- [v] Step 1: Finalize field rules
  - [v] `items.code` UNIQUE (yes)
  - [v] `items.barcode` UNIQUE (yes)
  - [v] `transactions.transaction_type` ∈ {OUT, IN, ADJUST}
  - [v] Timestamps default via `datetime('now')`

- [v] Step 2: Define tables (DDL draft)
  - [v] `product_groups` (id, name, parent_id, created_at)
  - [v] `items` (id, code UNIQUE, name, group_id, unit, barcode UNIQUE, current_stock, active, created_at, updated_at)
  - [v] `transactions` (id, transaction_number UNIQUE, person_name, transaction_type, notes, created_at)
  - [v] `transaction_items` (id, transaction_id, item_id, quantity, stock_before, stock_after)
  - [v] `stock_adjustments` (id, item_id, old_stock, new_stock, adjustment, reason, created_at)

- [v] Step 3: Indexes & foreign keys
  - [v] Indexes: items(name), items(code), items(barcode), transaction_items(transaction_id), product_groups(parent_id)
  - [v] Enable PRAGMA foreign_keys=ON
  - [v] `transaction_items.transaction_id` → `transactions.id` ON DELETE CASCADE

- [v] Step 4: Validate DDL
  - [v] Create schema in temporary DB file
  - [v] Verify constraints, indexes, and FK behavior

- [ ] Step 5: Document CSV mapping
  - [ ] CSV Item → items.name
  - [ ] CSV Stock → items.current_stock (coerce invalid to 0)
  - [ ] CSV Unit → items.unit
  - [ ] Duplicates policy: decide in migration step (keep first / sum / skip)

- [ ] Step 6: Record decisions
  - [ ] Save final DDL and decisions in repo notes/README

### 2.2 Database Layer Implementation
- [ ] Step 1: `DatabaseManager`
  - [ ] Open/close connection (context manager)
  - [ ] Ensure DB file directory exists
  - [ ] Enable `PRAGMA foreign_keys=ON` per connection
  - [ ] Provide helpers: `execute`, `executemany`, `query_all`, `query_one`
- [ ] Step 2: Initialization & migrations
  - [ ] Idempotent DDL runner (create tables/indexes if not exist)
  - [ ] Store current schema version (reserved for future upgrades)
  - [ ] Log warnings/errors to file on failure
- [ ] Step 3: Repositories (initial focus: Items)
  - [ ] `ItemsRepository`: `get_by_id`, `get_by_name`, `search(name LIKE)`, `insert`, `update`, `set_active`
  - [ ] Atomic stock update (`stock_before`/`stock_after` computed around print)
- [ ] Step 4: Transactions scaffolding
  - [ ] `TransactionManager` helper for BEGIN/COMMIT/ROLLBACK
  - [ ] Validate FK integrity on commit
- [ ] Step 5: Smoke tests/manual checks
  - [ ] Create temp DB, run migrations
  - [ ] Insert + query items
  - [ ] Verify cascade on `transaction_items`

### 2.3 CSV to SQLite Migration
- [ ] Step 1: Backup
  - [ ] Copy `data/barang.csv` → `data/barang.backup.csv`
- [ ] Step 2: Read CSV
  - [ ] Use pandas; coerce invalid stock to 0
- [ ] Step 3: Transform
  - [ ] Map: Item→items.name, Stock→items.current_stock, Unit→items.unit
  - [ ] Duplicates policy: keep first occurrence; log duplicates
- [ ] Step 4: Load
  - [ ] Batch insert rows into `items`
- [ ] Step 5: Verify
  - [ ] Count inserted vs. source (minus duplicates/invalid)
  - [ ] Spot-check several rows by name
- [ ] Step 6: Report
  - [ ] Print migration summary (inserted, skipped, duplicates)

### 2.4 Update Existing Code
- [ ] Step 1: Config flag
  - [ ] Add `data.source`: `"csv" | "sqlite"` (default: `"csv"`)
- [ ] Step 2: Repository adapter
  - [ ] Define `InventoryRepository` interface: `get_suggestions`, `get_item`, `update_stock`, `save`
  - [ ] CSV-backed adapter: proxy current `InventoryManager`
  - [ ] SQLite-backed adapter: wrap `ItemsRepository`
- [ ] Step 3: UI wiring (POSApp)
  - [ ] Choose backend by `data.source`
  - [ ] Keep identical UX and shortcuts
- [ ] Step 4: Testing
  - [ ] Verify search/add/edit/print/stock for both backends
  - [ ] Validate persistence in SQLite

**Deliverable**: Fully functional system using SQLite database, CSV deprecated

---

## Phase 3: Multi-Tab Interface
**Goal**: Transform single-window app into tabbed interface with navigation

### 3.1 Main Window Redesign
- [ ] Create main application window with sidebar navigation
- [ ] Implement tab/section switching mechanism
- [ ] Design navigation menu (similar to Aronium sidebar)
- [ ] Add section icons and labels

### 3.2 Navigation Sections
- [ ] Implement navigation items:
  - Main (Transaction entry)
  - Documents (Editable transaction history)
  - Products (Item management)
  - Stock (Stock levels view)
  - History (Read-only transaction view)
  - Reports (Analytics and exports)

### 3.3 Main Transaction Section (Refactor Current UI)
- [ ] Keep existing functionality in new tab structure
- [ ] Add "Person Name" input field
- [ ] Update layout to match Aronium style
- [ ] Improve cart display (remove price columns, add stock info)
- [ ] Update print button to save transaction to database

**Deliverable**: Multi-section interface with working Main transaction tab

---

## Phase 4: Transaction History & Management
**Goal**: Build transaction recording and history viewing capabilities

### 4.1 Transaction Recording
- [ ] Save each print action as a transaction record
- [ ] Generate unique transaction numbers
- [ ] Record person name with each transaction
- [ ] Save all items in transaction with quantities
- [ ] Record stock levels before/after transaction
- [ ] Add timestamp to all transactions

### 4.2 Documents Section (Editable History)
- [ ] Create Documents tab UI
- [ ] Display transaction list with filters:
  - Date range picker
  - Person name search
  - Transaction number search
- [ ] Show transaction details when selected
- [ ] Implement edit functionality:
  - Add items to existing transaction
  - Remove items from transaction
  - Change quantities
  - Update person name
- [ ] Add reprint button
- [ ] Implement delete transaction (with confirmation)
- [ ] Update stock levels when transactions are edited

### 4.3 History Section (Read-Only View)
- [ ] Create History tab UI (similar to Documents but read-only)
- [ ] Display all past transactions
- [ ] Add search and filter capabilities
- [ ] Show transaction details
- [ ] Add print/reprint functionality
- [ ] Prevent any editing

**Deliverable**: Complete transaction tracking with editable and read-only views

---

## Phase 5: Product Management
**Goal**: Build interface for managing items, groups, and units

### 5.1 Product Groups Management
- [ ] Create product groups tree view (left sidebar)
- [ ] Implement add/edit/delete group functionality
- [ ] Support nested groups (parent-child relationships)
- [ ] Add group filtering

### 5.2 Products Section UI
- [ ] Create Products tab with table view
- [ ] Display columns: Code | Name | Group | Barcode | Unit | Current Stock | Active | Updated
- [ ] Implement sorting by columns
- [ ] Add search/filter functionality

### 5.3 Product CRUD Operations
- [ ] Add "New Product" button and form
- [ ] Implement edit product (double-click or edit button)
- [ ] Add delete product (with confirmation)
- [ ] Support bulk operations (if needed)
- [ ] Validate product data (unique codes, required fields)

### 5.4 Product Import/Export
- [ ] Add "Import from CSV" functionality
- [ ] Add "Export to CSV" functionality
- [ ] Support Excel import/export (optional)

**Deliverable**: Full product management interface with CRUD operations

---

## Phase 6: Stock Management
**Goal**: View current stock levels and make manual adjustments

### 6.1 Stock Section UI
- [ ] Create Stock tab with table view
- [ ] Display columns: Code | Name | Group | Quantity | Unit | Last Updated | Last Transaction
- [ ] Add group filter (tree view on left)
- [ ] Implement search functionality
- [ ] Add color coding (red for negative, yellow for low stock)

### 6.2 Stock Adjustment Feature
- [ ] Add "Adjust Stock" button
- [ ] Create stock adjustment dialog
- [ ] Show current stock and allow new value input
- [ ] Calculate adjustment automatically (e.g., -5 → 10 = +15)
- [ ] Require reason/notes for adjustment
- [ ] Save adjustment as special transaction type
- [ ] Record in `stock_adjustments` table

### 6.3 Stock In/Out Tracking
- [ ] Implement "Stock In" transaction type
- [ ] Create simple form for receiving inventory
- [ ] Record person who received stock
- [ ] Update stock levels accordingly
- [ ] Differentiate between Stock Out (normal), Stock In, and Adjustments

### 6.4 Low Stock Alerts
- [ ] Add low stock threshold setting per item
- [ ] Highlight low stock items in red/yellow
- [ ] Add low stock filter/report
- [ ] Optional: notification system

**Deliverable**: Complete stock management with adjustments and tracking

---

## Phase 7: Reporting & Analytics
**Goal**: Build comprehensive reporting system with exports

### 7.1 Reports Section UI
- [ ] Create Reports tab
- [ ] Add report type selector (left panel)
- [ ] Implement filter panel (right side):
  - Date range picker
  - Product group filter
  - Product name filter
  - Person name filter
  - Transaction type filter

### 7.2 Core Reports Implementation
- [ ] **Stock Movement by Product Report**
  - Show which items went out/in during date range
  - Display: Product | Group | Quantity Out | Quantity In | Net Change | Unit
  - Group by product
  
- [ ] **Stock Movement by Time Report**
  - Daily/weekly/monthly summary
  - Display: Date | Total Items Moved | Total Quantity Out | Total Quantity In
  
- [ ] **Transaction History Report**
  - All transactions in date range
  - Display: Date | Transaction # | Person | Items Count | Total Qty
  
- [ ] **Stock Adjustments Report**
  - All manual stock changes
  - Display: Date | Product | Old Stock | New Stock | Adjustment | Reason | Person
  
- [ ] **Current Stock Levels Report**
  - Snapshot of all items
  - Display: Product | Group | Current Stock | Unit | Last Updated
  
- [ ] **Inactive Items Report**
  - Items with no movement in X days
  - Display: Product | Group | Stock | Last Transaction Date | Days Inactive

### 7.3 Print Preview
- [ ] Create print preview window
- [ ] Format reports for printing (headers, footers, page numbers)
- [ ] Add company info/logo to reports
- [ ] Implement page navigation
- [ ] Add zoom controls

### 7.4 Export Functionality
- [ ] Implement PDF export using reportlab or similar
- [ ] Implement Excel export using openpyxl
- [ ] Add CSV export option
- [ ] Allow user to choose export format
- [ ] Save exports to configurable location

**Deliverable**: Full reporting system with print preview and multiple export formats

---

## Phase 8: Polish & Optimization
**Goal**: Improve user experience and performance

### 8.1 UI/UX Improvements
- [ ] Apply consistent dark theme (similar to Aronium)
- [ ] Add keyboard shortcuts for common actions
- [ ] Improve loading indicators for slow operations
- [ ] Add tooltips for buttons and fields
- [ ] Implement undo/redo for critical operations

### 8.2 Performance Optimization
- [ ] Add database indexing for faster queries
- [ ] Implement pagination for large data sets
- [ ] Optimize search queries
- [ ] Add caching where appropriate
- [ ] Profile and optimize slow operations

### 8.3 Data Backup & Recovery
- [ ] Implement automatic database backup
- [ ] Add manual backup/restore functionality
- [ ] Create database repair utility
- [ ] Add data export for full backup

### 8.4 Receipt Improvements
- [ ] Save receipt text files to receipts folder
- [ ] Add receipt templates
- [ ] Support custom receipt formats
- [ ] Add receipt reprinting from history

### 8.5 Testing & Bug Fixes
- [ ] Test all features thoroughly
- [ ] Fix any discovered bugs
- [ ] Test edge cases (negative stock, large quantities, etc.)
- [ ] Validate data integrity

**Deliverable**: Polished, production-ready application

---

## Phase 9: Advanced Features (Optional)
**Goal**: Add nice-to-have features based on usage

### 9.1 Barcode Support
- [ ] Add barcode scanner integration
- [ ] Support barcode search in main transaction screen
- [ ] Generate barcodes for items
- [ ] Print barcode labels

### 9.2 Multi-User Support
- [ ] Add user authentication (simple login)
- [ ] Track which user performed actions
- [ ] Add user permissions (view-only, edit, admin)

### 9.3 Dashboard
- [ ] Create dashboard section
- [ ] Show key metrics (total items, recent transactions, low stock count)
- [ ] Add charts/graphs for stock trends
- [ ] Display recent activity

### 9.4 Advanced Reporting
- [ ] Stock turnover analysis
- [ ] Trend analysis (which items move fastest)
- [ ] Seasonal patterns
- [ ] Custom report builder

**Deliverable**: Enhanced system with advanced capabilities

---

## Technical Stack

### Current
- Python 3.x
- Tkinter (GUI)
- Pandas (CSV handling)
- python-escpos (thermal printer)

### After Migration
- Python 3.x
- Tkinter (GUI)
- SQLite3 (database)
- python-escpos (thermal printer)
- reportlab (PDF generation)
- openpyxl (Excel export)

---

## Development Guidelines

### Working Approach
1. **One phase at a time**: Complete each phase before moving to next
2. **Test after each task**: Ensure nothing breaks
3. **Keep backups**: Backup database before major changes
4. **Commit frequently**: Use git for version control
5. **Document as you go**: Update comments and docs

### Testing Checklist (After Each Phase)
- [ ] All existing features still work
- [ ] New features work as expected
- [ ] No errors in console/logs
- [ ] Database integrity maintained
- [ ] UI is responsive and intuitive

### When to Ask for Help
- Stuck on a task for more than 2 hours
- Unsure about design decisions
- Need clarification on requirements
- Encountering unexpected errors

---

## Timeline Estimate
Based on weekly development (4-8 hours per week):

- **Phase 1**: 2-3 weeks
- **Phase 2**: 3-4 weeks
- **Phase 3**: 2-3 weeks
- **Phase 4**: 3-4 weeks
- **Phase 5**: 2-3 weeks
- **Phase 6**: 2-3 weeks
- **Phase 7**: 4-5 weeks
- **Phase 8**: 2-3 weeks
- **Phase 9**: Optional, 4-6 weeks

**Total**: ~20-30 weeks (5-7 months) for core features (Phases 1-8)

---

## Success Criteria

### Must Have (Core Features)
✓ SQLite database with transaction history
✓ Multi-tab interface with navigation
✓ Transaction recording with person names
✓ Editable and read-only transaction history
✓ Product management (CRUD)
✓ Stock level viewing and adjustments
✓ Basic reporting with date range filters
✓ PDF and Excel export

### Nice to Have (Optional)
- Barcode scanner support
- Multi-user authentication
- Dashboard with charts
- Advanced analytics

---

## Notes
- This roadmap is flexible - adjust based on actual progress and needs
- Some tasks may be combined or split as needed
- Priority is keeping the system working at all times
- Focus on core inventory tracking, not sales features
- Keep the interface simple and fast for daily use

---

**Last Updated**: November 8, 2025
**Status**: Planning Phase
**Next Step**: Begin Phase 1 - Foundation & Code Refactoring
