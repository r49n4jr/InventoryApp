import logging
import tkinter as tk
from tkinter import ttk, messagebox
from models.inventory_manager import InventoryManager
from utils.receipt_printer import ReceiptPrinter
from ui.autocomplete_entry import AutocompleteEntry
from config.manager import ConfigManager
from ui.settings_dialog import SettingsDialog
from utils.constants import (
    TITLE_NOT_FOUND,
    TITLE_INVALID_QUANTITY,
    TITLE_CONFIRM,
    TITLE_PRINT,
    TITLE_SAVE_ERROR,
    MSG_NOT_FOUND,
    MSG_INVALID_QTY_NONNEG,
    MSG_INVALID_QTY_INT,
    MSG_PRINT_CONFIRM,
    MSG_CLEAR_CONFIRM,
)
from ui.common import confirm_modal

logger = logging.getLogger(__name__)

class POSApp:
    """Tkinter-based POS UI for searching items, printing receipts, and updating stock."""
    def __init__(self, root):
        """Initialize the application and load configuration, data, and printer.

        Args:
            root: Tk root window.
        """
        self.root = root
        self.config = ConfigManager()
        self.manager = InventoryManager(self.config.csv_path)
        self.printer = ReceiptPrinter(
            self.config.printer_port,
            baudrate=self.config.printer_baudrate,
            timeout=self.config.printer_timeout,
        )
        self.columns = ("Item", "Stock", "Qty", "Unit")
        self.qty_var = tk.StringVar(value="1")
        self.search_var = tk.StringVar()

        self.setup_ui()

    def setup_ui(self):
        """Build the window title, menu, table, search bar, buttons, and shortcuts."""
        self.update_title()
        self.root.geometry("600x580")

        # Menu bar with Settings
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        app_menu = tk.Menu(menubar, tearoff=0)
        app_menu.add_command(label="Settings", command=self.open_settings)
        menubar.add_cascade(label="App", menu=app_menu)

        self.setup_treeview()
        self.setup_search_bar()
        self.setup_buttons()
        self.setup_shortcuts()

    def setup_treeview(self):
        """Create the items Treeview and configure columns and scrollbar."""
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(expand=True, fill="both", padx=10, pady=10)

        tree_scroll = tk.Scrollbar(tree_frame)
        tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(tree_frame, columns=self.columns, show="headings", yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=self.tree.yview)
        self.tree.pack(side="left", expand=True, fill="both")

        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

    def setup_search_bar(self):
        """Create quantity input and autocomplete search entry."""
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Qty:").pack(side="left", padx=5)
        self.qty_entry = tk.Entry(search_frame, textvariable=self.qty_var, width=5)
        self.qty_entry.pack(side="left")
        self.qty_entry.focus()
        self.qty_entry.select_range(0, tk.END)

        tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = AutocompleteEntry(
            self.manager.get_suggestions,
            self.search_items,
            self.qty_entry,
            search_frame,
            textvariable=self.search_var
        )
        self.search_entry.pack(side="left", fill="x", expand=True)

    def setup_buttons(self):
        """Create primary action buttons for qty, print, remove, and clear."""
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Qty (F4)", command=self.edit_quantity).pack(side="left", padx=10)
        tk.Button(button_frame, text="Print (F12)", command=self.print_receipt).pack(side="left", padx=10)
        tk.Button(button_frame, text="Remove (Backspace)", command=self.remove_selected).pack(side="left", padx=10)
        tk.Button(button_frame, text="Cancel (Del)", command=self.remove_all).pack(side="left", padx=10)

    def setup_shortcuts(self):
        """Bind keyboard shortcuts for core actions."""
        self.root.bind("<F4>", lambda e: self.edit_quantity())
        self.root.bind("<F12>", lambda e: self.print_receipt())
        self.root.bind("<BackSpace>", lambda e: self.remove_selected())
        self.root.bind("<Delete>", lambda e: self.remove_all())

    def remove_selected(self):
        """Remove selected rows from the cart list and refocus quantity entry."""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        for item_id in selected_items:
            self.tree.delete(item_id)
        self.focus_qty()

    def open_settings(self):
        """Open the settings dialog and apply changes when saved."""
        SettingsDialog(self.root, self.config, on_saved=self.apply_config)

    def apply_config(self):
        """Reload configuration and recreate dependent components (title, data, printer)."""
        # Reload config from disk and apply to app
        self.config.load()
        # Update title
        self.update_title()
        # Recreate manager with potentially new CSV path
        self.manager = InventoryManager(self.config.csv_path)
        # Recreate printer with new settings
        self.printer = ReceiptPrinter(
            self.config.printer_port,
            baudrate=self.config.printer_baudrate,
            timeout=self.config.printer_timeout,
        )

    def update_title(self):
        """Compute and set the window title from current configuration."""
        title = self.config.app_name or "Inventory App"
        if self.config.company_name:
            title = f"{title} - {self.config.company_name}"
        self.root.title(title)

    def focus_qty(self):
        """Focus the quantity entry and select its content."""
        self.qty_entry.focus()
        self.qty_entry.select_range(0, tk.END)

    def search_items(self, keyword=None):
        """Search the inventory and add or update an item row in the cart.

        Args:
            keyword: Text to search for; provided by autocomplete on selection or Enter.
        """
        row = self.manager.get_item(keyword)
        if row is None:
            messagebox.showinfo(TITLE_NOT_FOUND, MSG_NOT_FOUND.format(keyword=keyword))
            self.reset_search()
            return
        item_name = row["Item"]
        stock = row["Stock"]
        unit = row.get("Unit", self.config.default_unit)
        try:
            qty = int(self.qty_var.get())
            if qty < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(TITLE_INVALID_QUANTITY, MSG_INVALID_QTY_NONNEG)
            self.qty_var.set("1")
            self.qty_entry.focus()
            return
        for item_id in self.tree.get_children():
            values = self.tree.item(item_id)["values"]
            if values[0] == item_name:
                new_values = list(values)
                new_values[2] = int(new_values[2]) + qty
                self.tree.item(item_id, values=new_values)
                self.reset_search()
                return
        self.tree.insert("", "end", values=(item_name, stock, qty, unit))
        self.reset_search()

    def edit_quantity(self):
        """Open a popup to edit the quantity of the currently selected item."""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        selected = selected_items[0]
        item_data = self.tree.item(selected)["values"]
        current_qty = item_data[2]

        qty_window = tk.Toplevel(self.root)
        qty_window.title("Edit Quantity")
        qty_window.geometry("250x100")
        qty_window.grab_set()

        tk.Label(qty_window, text="Enter Quantity:").pack(pady=5)
        qty_entry_popup = tk.Entry(qty_window)
        qty_entry_popup.insert(0, str(current_qty))
        qty_entry_popup.select_range(0, tk.END)
        qty_entry_popup.pack()
        qty_entry_popup.focus()

        def save_qty(event=None):
            try:
                new_qty = int(qty_entry_popup.get())
                if new_qty <= 0:
                    self.tree.delete(selected)
                else:
                    item_data[2] = new_qty
                    self.tree.item(selected, values=item_data)
                qty_window.destroy()
                self.focus_qty()
            except ValueError:
                messagebox.showerror(TITLE_INVALID_QUANTITY, MSG_INVALID_QTY_INT)

        qty_entry_popup.bind("<Return>", save_qty)

    def remove_all(self):
        """Clear the cart after user confirmation and refocus quantity entry."""
        # Confirm clearing all items
        if not confirm_modal(self.root, TITLE_CONFIRM, MSG_CLEAR_CONFIRM):
            return
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        self.focus_qty()

    def print_receipt(self):
        """Print the current cart to the receipt printer and persist stock updates."""
        all_items = self.tree.get_children()
        if not all_items:
            return
        # Confirm printing
        if not confirm_modal(self.root, TITLE_PRINT, MSG_PRINT_CONFIRM):
            return
        items = []
        for item_id in all_items:
            item_data = self.tree.item(item_id)["values"]
            item_name, stock, qty, unit = item_data
            items.append((item_name, stock, qty, unit))
        success = self.printer.print(items)
        if not success:
            return
        try:
            for item_name, stock, qty, unit in items:
                new_stock = int(stock) - int(qty)
                self.manager.update_stock(item_name, new_stock)
            self.manager.save()
        except Exception as e:
            messagebox.showerror(TITLE_SAVE_ERROR, f"Failed to update stock:\n{e}")
            return
        self.remove_all()

    def reset_search(self):
        """Clear search field, reset qty to 1, and focus qty entry."""
        self.search_var.set("")
        self.qty_var.set("1")
        self.focus_qty()
