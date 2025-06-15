import os
from datetime import datetime
from typing import Optional
import sys

COLORS = {
    'INFO': '\033[94m',
    'WARNING': '\033[93m',
    'ERROR': '\033[91m',
    'RESET': '\033[0m',
}

LOG_DIR = "./log"
LOG_FILE = None

def _ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)

def _get_log_path():
    timestamp = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"{timestamp}.log")

def log(message: str, level: str = "INFO", console: bool = True, file: Optional[bool] = None):
    global LOG_FILE

    if level not in COLORS:
        level = "INFO"  # fallback protection

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    text = f"{timestamp} - {level} - {message}"

    if console:
        colored = f"{COLORS[level]}{text}{COLORS['RESET']}"
        print(colored)

    if file is not False:
        if LOG_FILE is None:
            _ensure_log_dir()
            LOG_FILE = _get_log_path()
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(text + '\n')
        except Exception as e:
            print(f"Logging failed: {e}", file=sys.stderr)
