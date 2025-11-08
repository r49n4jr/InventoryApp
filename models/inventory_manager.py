import logging
import pandas as pd
from tkinter import messagebox
from utils.constants import TITLE_INVENTORY_ERROR, TITLE_SAVE_ERROR

logger = logging.getLogger(__name__)

class InventoryManager:
    """Manage inventory data stored in a CSV file.

    Attributes:
        path: Path to the CSV file.
        df: In-memory pandas DataFrame of inventory rows.
    """
    def __init__(self, path):
        """Initialize the manager and load inventory from CSV.

        Args:
            path: CSV file path.
        """
        self.path = path
        self.df = pd.DataFrame()
        self.load()

    def load(self):
        """Load the inventory from disk, creating a new file if missing.

        Ensures required columns exist; logs and shows user-friendly
        messages on errors and initializes an empty structure on failure.
        """
        try:
            try:
                self.df = pd.read_csv(self.path)
                if not {"Item", "Stock"}.issubset(self.df.columns):
                    raise ValueError("Missing required columns in CSV")
                logger.info("Loaded inventory from %s (%d rows)", self.path, len(self.df))
            except FileNotFoundError:
                logger.warning("Inventory file not found at %s. Creating a new one.", self.path)
                self.df = pd.DataFrame({"Item": [], "Stock": [], "Unit": []})
                self.save()
            except Exception as e:
                logger.exception("Failed reading inventory from %s", self.path)
                messagebox.showerror(TITLE_INVENTORY_ERROR, f"Failed to read inventory at {self.path}. Initializing empty list.\n{e}")
                self.df = pd.DataFrame({"Item": [], "Stock": [], "Unit": []})
        except Exception as e:
            logger.exception("Inventory load failed")
            messagebox.showerror(TITLE_INVENTORY_ERROR, f"Import failed:\n{e}")

    def get_suggestions(self, keyword):
        """Return a list of item name suggestions matching the keyword.

        Matching is case-insensitive plain text against the Item column.

        Args:
            keyword: Text typed by the user.

        Returns:
            List of item names.
        """
        if keyword is None:
            return []
        keyword = str(keyword).strip()
        if not keyword:
            return []
        if "Item" not in self.df.columns:
            return []
        col = self.df["Item"].astype(str)
        matches = self.df[col.str.contains(keyword, case=False, regex=False, na=False)]
        return list(matches["Item"]) if not matches.empty else []

    def get_item(self, keyword):
        """Return the first row matching the keyword or None if not found.

        Args:
            keyword: Search text.

        Returns:
            pandas.Series of the first match, or None.
        """
        if keyword is None:
            return None
        keyword = str(keyword).strip()
        if not keyword:
            return None
        if "Item" not in self.df.columns:
            return None
        col = self.df["Item"].astype(str)
        matches = self.df[col.str.contains(keyword, case=False, regex=False, na=False)]
        return matches.iloc[0] if not matches.empty else None

    def update_stock(self, item_name, new_stock):
        """Update stock quantity for the given item name.

        Args:
            item_name: The item name to update.
            new_stock: New stock value (int).
        """
        self.df.loc[self.df["Item"] == item_name, "Stock"] = new_stock

    def save(self):
        """Persist the inventory DataFrame to the CSV file."""
        try:
            self.df.to_csv(self.path, index=False)
            logger.info("Saved inventory to %s (%d rows)", self.path, len(self.df))
        except Exception as e:
            logger.exception("Failed saving inventory to %s", self.path)
            messagebox.showerror(TITLE_SAVE_ERROR, f"Failed to save inventory to {self.path}:\n{e}")
