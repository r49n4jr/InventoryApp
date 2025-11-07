import datetime
from escpos.printer import Serial
from tkinter import messagebox

class ReceiptPrinter:
    def __init__(self, port):
        self.port = port

    def print(self, items):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        total_qty = sum(int(qty) for _, _, qty, _ in items)

        try:
            printer = Serial(devfile=self.port, baudrate=9600, timeout=1)
            printer.set(align='center')
            printer.text("Barang Gudang\n")
            printer.text(f"{timestamp}\n\n")

            printer.set(align='left')
            for item_name, _, qty, unit in items:
                printer.text(f"{qty} {unit} - {item_name}\n")  # 👈 No extra newline

            printer.text(f"\nTotal Qty: {total_qty}\n")
            printer.cut(mode='FULL')

        except Exception as e:
            messagebox.showerror("Print Error", f"Could not print:\n{e}")
