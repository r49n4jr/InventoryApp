# Shared constants used across the application

# Application defaults
APP_DEFAULT_NAME = "Barang Gudang"
DEFAULT_UNIT = "pcs"

# Data paths (relative to project root by default)
DEFAULT_CSV_PATH = "data/barang.csv"
DEFAULT_DB_PATH = "db/app.db"

# Printer defaults
DEFAULT_PRINTER_PORT = "COM6"
DEFAULT_PRINTER_BAUDRATE = 9600
DEFAULT_PRINTER_TIMEOUT = 1

# Logging
LOGS_DIR = "logs"
APP_LOG_FILE = "app.log"

# UI message titles
TITLE_INVALID_SETTINGS = "Invalid Settings"
TITLE_INVALID_QUANTITY = "Invalid Quantity"
TITLE_NOT_FOUND = "Not Found"
TITLE_PRINT = "Print"
TITLE_CONFIRM = "Confirm"
TITLE_PRINT_ERROR = "Print Error"
TITLE_SAVE_ERROR = "Save Error"
TITLE_CONFIG_ERROR = "Config Error"
TITLE_INVENTORY_ERROR = "Inventory Error"

# UI message bodies
MSG_INVALID_QTY_NONNEG = "Please enter a valid non-negative integer for quantity."
MSG_INVALID_QTY_INT = "Please enter a valid integer quantity."
MSG_NOT_FOUND = "No item found matching: {keyword}"
MSG_PRINT_CONFIRM = "Print the receipt and update stock?"
MSG_CLEAR_CONFIRM = "Clear all items from the cart?"
