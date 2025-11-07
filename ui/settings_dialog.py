import tkinter as tk
from tkinter import ttk, filedialog
from config.manager import ConfigManager

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, config: ConfigManager, on_saved=None):
        super().__init__(parent)
        self.title("Settings")
        self.resizable(False, False)
        self.grab_set()
        self.config_manager = config
        self.on_saved = on_saved

        pad = {"padx": 8, "pady": 4}

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        # App info
        ttk.Label(frm, text="Application Name").grid(row=0, column=0, sticky="w", **pad)
        self.app_name_var = tk.StringVar(value=self.config_manager.app_name)
        ttk.Entry(frm, textvariable=self.app_name_var, width=36).grid(row=0, column=1, **pad)

        ttk.Label(frm, text="Company Name").grid(row=1, column=0, sticky="w", **pad)
        self.company_var = tk.StringVar(value=self.config_manager.company_name)
        ttk.Entry(frm, textvariable=self.company_var, width=36).grid(row=1, column=1, **pad)

        # Printer
        ttk.Label(frm, text="Printer Port").grid(row=2, column=0, sticky="w", **pad)
        self.printer_port_var = tk.StringVar(value=self.config_manager.printer_port)
        ttk.Entry(frm, textvariable=self.printer_port_var, width=20).grid(row=2, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Baudrate").grid(row=3, column=0, sticky="w", **pad)
        self.baudrate_var = tk.IntVar(value=self.config_manager.printer_baudrate)
        ttk.Entry(frm, textvariable=self.baudrate_var, width=10).grid(row=3, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Timeout (s)").grid(row=4, column=0, sticky="w", **pad)
        self.timeout_var = tk.IntVar(value=self.config_manager.printer_timeout)
        ttk.Entry(frm, textvariable=self.timeout_var, width=10).grid(row=4, column=1, sticky="w", **pad)

        # Data
        ttk.Label(frm, text="CSV Path").grid(row=5, column=0, sticky="w", **pad)
        self.csv_path_var = tk.StringVar(value=self.config_manager.csv_path)
        csv_row = ttk.Frame(frm)
        csv_row.grid(row=5, column=1, sticky="w", **pad)
        ttk.Entry(csv_row, textvariable=self.csv_path_var, width=28).pack(side="left")
        ttk.Button(csv_row, text="Browse", command=self.browse_csv).pack(side="left", padx=4)

        ttk.Label(frm, text="DB Path").grid(row=6, column=0, sticky="w", **pad)
        self.db_path_var = tk.StringVar(value=self.config_manager.db_path)
        db_row = ttk.Frame(frm)
        db_row.grid(row=6, column=1, sticky="w", **pad)
        ttk.Entry(db_row, textvariable=self.db_path_var, width=28).pack(side="left")
        ttk.Button(db_row, text="Browse", command=self.browse_db).pack(side="left", padx=4)

        ttk.Label(frm, text="Default Unit").grid(row=7, column=0, sticky="w", **pad)
        self.unit_var = tk.StringVar(value=self.config_manager.default_unit)
        ttk.Entry(frm, textvariable=self.unit_var, width=12).grid(row=7, column=1, sticky="w", **pad)

        # Actions
        btns = ttk.Frame(frm)
        btns.grid(row=8, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="right")
        ttk.Button(btns, text="Save", command=self.save).pack(side="right", padx=8)

        self.bind("<Escape>", lambda e: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def browse_csv(self):
        path = filedialog.askopenfilename(title="Select CSV", filetypes=[("CSV", "*.csv"), ("All files", "*.*")])
        if path:
            self.csv_path_var.set(path)

    def browse_db(self):
        path = filedialog.asksaveasfilename(title="Select DB Path", defaultextension=".db", filetypes=[("SQLite DB", "*.db"), ("All files", "*.*")])
        if path:
            self.db_path_var.set(path)

    def save(self):
        data = {
            "app_name": self.app_name_var.get().strip() or "Inventory App",
            "company_name": self.company_var.get().strip(),
            "printer": {
                "port": self.printer_port_var.get().strip() or "COM6",
                "baudrate": int(self.baudrate_var.get()),
                "timeout": int(self.timeout_var.get()),
            },
            "data": {
                "csv_path": self.csv_path_var.get().strip() or "data/barang.csv",
                "db_path": self.db_path_var.get().strip() or "db/app.db",
                "default_unit": self.unit_var.get().strip() or "pcs",
            },
        }
        self.config_manager._data = data
        self.config_manager.save()
        if self.on_saved:
            self.on_saved()
        self.destroy()
