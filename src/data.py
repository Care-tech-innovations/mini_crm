import json
import os
import shutil
import tempfile
import glob
from datetime import datetime

try:
    from filelock import FileLock
    HAS_FILELOCK = True
except ImportError:
    HAS_FILELOCK = False

# Project root (parent of src/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "clients.json")
LOCK_FILE = os.path.join(BASE_DIR, "clients.json.lock")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
MAX_BACKUPS = 10

VALID_STATUSES = ["interested", "student", "client"]


def default_data():
    return {"next_id": 1, "clients": []}


def _validate_data(data):
    """Validate data structure. Raises ValueError if invalid."""
    if not isinstance(data, dict):
        raise ValueError("Data must be a dict")
    if "clients" not in data:
        raise ValueError("Data must contain 'clients' key")
    if not isinstance(data["clients"], list):
        raise ValueError("'clients' must be a list")
    return data


def _create_backup():
    """Create a timestamped backup of clients.json before overwriting."""
    if not os.path.exists(DATA_FILE):
        return
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"clients_{timestamp}.json")
    shutil.copy2(DATA_FILE, backup_path)
    # Rotate: delete oldest backups if too many
    backups = sorted(glob.glob(os.path.join(BACKUP_DIR, "clients_*.json")))
    for old in backups[:-MAX_BACKUPS]:
        try:
            os.remove(old)
        except OSError:
            pass


def load_data():
    """Load client data. Falls back to latest backup if main file is corrupted."""
    # Try main file first
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return _validate_data(data)
        except (json.JSONDecodeError, IOError, ValueError):
            pass  # Fall through to backup

    # Try latest backup
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backups = sorted(
        glob.glob(os.path.join(BACKUP_DIR, "clients_*.json")),
        reverse=True,
    )
    for backup_path in backups:
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return _validate_data(data)
        except (json.JSONDecodeError, IOError, ValueError):
            continue

    return default_data()


def save_data(data):
    """Save data with atomic write and automatic backup."""
    _validate_data(data)
    _create_backup()

    def _do_save():
        temp_fd, temp_path = tempfile.mkstemp(suffix=".json", dir=BASE_DIR)
        try:
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            shutil.move(temp_path, DATA_FILE)
        except Exception:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            raise

    if HAS_FILELOCK:
        with FileLock(LOCK_FILE, timeout=10):
            _do_save()
    else:
        _do_save()


def reorganize_ids(data):
    data["clients"].sort(key=lambda c: c["name"].lower())
    for i, client in enumerate(data["clients"], 1):
        client["id"] = i
    data["next_id"] = len(data["clients"]) + 1


def find_client_by_id(clients, client_id):
    for client in clients:
        if client["id"] == client_id:
            return client
    return None
