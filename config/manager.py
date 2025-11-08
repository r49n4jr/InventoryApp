import json
import logging
from pathlib import Path
from tkinter import messagebox
from utils.constants import (
    APP_DEFAULT_NAME,
    DEFAULT_PRINTER_BAUDRATE,
    DEFAULT_PRINTER_PORT,
    DEFAULT_PRINTER_TIMEOUT,
    DEFAULT_CSV_PATH,
    DEFAULT_DB_PATH,
    DEFAULT_UNIT,
    TITLE_CONFIG_ERROR,
)

logger = logging.getLogger(__name__)

class ConfigManager:
    """Load and persist application configuration in a JSON file."""
    def __init__(self, path: str | Path = Path(__file__).with_name("config.json")):
        """Initialize the configuration manager and load config from disk.

        Args:
            path: Path to the JSON configuration file.
        """
        self.path = Path(path)
        self._data = {}
        self.load()

    def load(self):
        """Load the configuration from disk or create defaults if missing.

        Shows a user-friendly error and recreates defaults for malformed JSON.
        """
        try:
            if not self.path.exists():
                logger.warning("Config not found at %s. Creating default config.", self.path)
                self._data = {
                    "app_name": APP_DEFAULT_NAME,
                    "company_name": "",
                    "printer": {"port": DEFAULT_PRINTER_PORT, "baudrate": DEFAULT_PRINTER_BAUDRATE, "timeout": DEFAULT_PRINTER_TIMEOUT},
                    "data": {"csv_path": DEFAULT_CSV_PATH, "db_path": DEFAULT_DB_PATH, "default_unit": DEFAULT_UNIT},
                }
                self.save()
                return
            with self.path.open("r", encoding="utf-8") as f:
                self._data = json.load(f)
        except json.JSONDecodeError as e:
            logger.exception("Malformed config at %s", self.path)
            messagebox.showerror(TITLE_CONFIG_ERROR, f"Config file is corrupted. Recreating defaults.\n{e}")
            self._data = {
                "app_name": APP_DEFAULT_NAME,
                "company_name": "",
                "printer": {"port": DEFAULT_PRINTER_PORT, "baudrate": DEFAULT_PRINTER_BAUDRATE, "timeout": DEFAULT_PRINTER_TIMEOUT},
                "data": {"csv_path": DEFAULT_CSV_PATH, "db_path": DEFAULT_DB_PATH, "default_unit": DEFAULT_UNIT},
            }
            self.save()
        except Exception as e:
            logger.exception("Failed loading config from %s", self.path)
            messagebox.showerror(TITLE_CONFIG_ERROR, f"Failed to load config: {self.path}\n{e}")

    def save(self):
        """Save the in-memory configuration to disk."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            logger.info("Saved config to %s", self.path)
        except Exception as e:
            logger.exception("Failed saving config to %s", self.path)
            messagebox.showerror(TITLE_CONFIG_ERROR, f"Failed to save config: {self.path}\n{e}")

    # Convenience getters
    @property
    def app_name(self) -> str:
        """Application display name."""
        return self._data.get("app_name", APP_DEFAULT_NAME)

    @property
    def company_name(self) -> str:
        """Company name string appended to the window title."""
        return self._data.get("company_name", "")

    @property
    def printer_port(self) -> str:
        """Serial port name for the ESC/POS printer (e.g., COM6)."""
        return self._data.get("printer", {}).get("port", DEFAULT_PRINTER_PORT)

    @property
    def printer_baudrate(self) -> int:
        """Serial baudrate for the printer."""
        return int(self._data.get("printer", {}).get("baudrate", DEFAULT_PRINTER_BAUDRATE))

    @property
    def printer_timeout(self) -> int:
        """Serial read/write timeout (seconds) for the printer."""
        return int(self._data.get("printer", {}).get("timeout", DEFAULT_PRINTER_TIMEOUT))

    @property
    def csv_path(self) -> str:
        """Path to the CSV file storing inventory data."""
        return self._data.get("data", {}).get("csv_path", DEFAULT_CSV_PATH)

    @property
    def db_path(self) -> str:
        """Path to the SQLite database file (future migration)."""
        return self._data.get("data", {}).get("db_path", DEFAULT_DB_PATH)

    @property
    def default_unit(self) -> str:
        """Default unit string when an item row lacks a Unit value."""
        return self._data.get("data", {}).get("default_unit", DEFAULT_UNIT)
