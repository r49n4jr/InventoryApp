import datetime
from escpos.printer import Serial
from tkinter import messagebox
import logging
import time
from utils.constants import TITLE_PRINT_ERROR

logger = logging.getLogger(__name__)

class ReceiptPrinter:
    """Light wrapper around ESC/POS serial printer for receipt printing."""
    def __init__(self, port, baudrate: int = 9600, timeout: int = 1):
        """Create a printer interface.

        Args:
            port: Serial port (e.g., 'COM6' on Windows).
            baudrate: Serial baudrate.
            timeout: Serial timeout in seconds.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

    def print(self, items):
        """Print a simple receipt.

        Args:
            items: Iterable of tuples (item_name, stock_before, qty, unit).

        Returns:
            True if printed successfully, False otherwise.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        total_qty = sum(int(qty) for _, _, qty, _ in items)

        logger.info("Printing receipt on %s with %d items", self.port, len(items))
        attempts = 2
        for attempt in range(1, attempts + 1):
            try:
                printer = Serial(devfile=self.port, baudrate=self.baudrate, timeout=self.timeout)
                printer.set(align='center')
                printer.text("Barang Gudang\n")
                printer.text(f"{timestamp}\n\n")

                printer.set(align='left')
                for item_name, _, qty, unit in items:
                    printer.text(f"{qty} {unit} - {item_name}\n")

                printer.text(f"\nTotal Qty: {total_qty}\n")
                printer.cut(mode='FULL')
                logger.info("Print successful")
                return True
            except Exception as e:
                logger.exception("Print attempt %d/%d failed", attempt, attempts)
                if attempt < attempts:
                    time.sleep(0.5)
                    continue
                messagebox.showerror(TITLE_PRINT_ERROR, f"Could not print:\n{e}")
                return False
