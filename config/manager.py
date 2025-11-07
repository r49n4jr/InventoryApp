import json
from pathlib import Path

class ConfigManager:
    def __init__(self, path: str | Path = Path(__file__).with_name("config.json")):
        self.path = Path(path)
        self._data = {}
        self.load()

    def load(self):
        if not self.path.exists():
            # Create default config if missing
            self._data = {
                "app_name": "Barang Gudang",
                "company_name": "",
                "printer": {"port": "COM6", "baudrate": 9600, "timeout": 1},
                "data": {"csv_path": "data/barang.csv", "db_path": "db/app.db", "default_unit": "pcs"},
            }
            self.save()
            return
        with self.path.open("r", encoding="utf-8") as f:
            self._data = json.load(f)

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    # Convenience getters
    @property
    def app_name(self) -> str:
        return self._data.get("app_name", "Barang Gudang")

    @property
    def company_name(self) -> str:
        return self._data.get("company_name", "")

    @property
    def printer_port(self) -> str:
        return self._data.get("printer", {}).get("port", "COM6")

    @property
    def printer_baudrate(self) -> int:
        return int(self._data.get("printer", {}).get("baudrate", 9600))

    @property
    def printer_timeout(self) -> int:
        return int(self._data.get("printer", {}).get("timeout", 1))

    @property
    def csv_path(self) -> str:
        return self._data.get("data", {}).get("csv_path", "data/barang.csv")

    @property
    def db_path(self) -> str:
        return self._data.get("data", {}).get("db_path", "db/app.db")

    @property
    def default_unit(self) -> str:
        return self._data.get("data", {}).get("default_unit", "pcs")
