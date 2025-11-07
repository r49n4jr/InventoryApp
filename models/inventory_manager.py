import pandas as pd
from tkinter import messagebox

class InventoryManager:
    def __init__(self, path):
        self.path = path
        self.df = pd.DataFrame()
        self.load()

    def load(self):
        try:
            # Ensure file exists with required headers
            try:
                self.df = pd.read_csv(self.path)
            except FileNotFoundError:
                self.df = pd.DataFrame({"Item": [], "Stock": [], "Unit": []})
                self.save()
            except Exception:
                # If file exists but unreadable, show error and init empty structure
                messagebox.showerror("Error", f"Failed to read inventory at {self.path}. Initializing empty list.")
                self.df = pd.DataFrame({"Item": [], "Stock": [], "Unit": []})
        except Exception as e:
            messagebox.showerror("Error", f"Import failed:\n{e}")

    def get_suggestions(self, keyword):
        keyword = keyword.lower()
        matches = self.df[self.df.apply(
            lambda row: keyword in " ".join(str(v).lower() for v in row), axis=1)]
        return list(matches["Item"]) if not matches.empty else []

    def get_item(self, keyword):
        keyword = keyword.lower()
        matches = self.df[self.df.apply(
            lambda row: keyword in " ".join(str(v).lower() for v in row), axis=1)]
        return matches.iloc[0] if not matches.empty else None

    def update_stock(self, item_name, new_stock):
        self.df.loc[self.df["Item"] == item_name, "Stock"] = new_stock

    def save(self):
        self.df.to_csv(self.path, index=False)
