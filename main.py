import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from tkinter import Tk
from ui.pos_app import POSApp
from utils.constants import LOGS_DIR, APP_LOG_FILE

# Setup logging (file-based with rotation)
logs_dir = Path(LOGS_DIR)
logs_dir.mkdir(exist_ok=True)
log_file = logs_dir / APP_LOG_FILE

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Avoid duplicate handlers if reloaded
if not logger.handlers:
    file_handler = RotatingFileHandler(log_file, maxBytes=512_000, backupCount=3, encoding="utf-8")
    console_handler = logging.StreamHandler()
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    file_handler.setFormatter(fmt)
    console_handler.setFormatter(fmt)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

logging.info("Application starting")

root = Tk()
app = POSApp(root)
root.mainloop()
