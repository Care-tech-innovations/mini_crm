"""
Data layer: load and save clients via Supabase.
Falls back to JSON file if Supabase credentials are not configured.
"""

import json
import os
import shutil
import tempfile
import glob
from datetime import datetime

# Load .env for local development (Streamlit Cloud uses st.secrets)
try:
    from dotenv import load_dotenv
    _base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(_base_dir, ".env"))
except ImportError:
    pass

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

TABLE_NAME = "Ramayana's Clients"  # Must match your Supabase table name


def _get_supabase_client():
    """Get Supabase client. Returns None if credentials not configured."""
    url = None
    key = None

    try:
        import streamlit as st
        if hasattr(st, "secrets") and st.secrets:
            url = st.secrets.get("SUPABASE_URL")
            key = st.secrets.get("SUPABASE_KEY")
    except Exception:
        pass

    if not url or not key:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        return None

    try:
        from supabase import create_client
        return create_client(url, key)
    except Exception:
        return None


def _use_supabase():
    """Check if we should use Supabase (credentials available)."""
    return _get_supabase_client() is not None


# ── JSON fallback (original logic) ───────────────────────────────────────────

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
    backups = sorted(glob.glob(os.path.join(BACKUP_DIR, "clients_*.json")))
    for old in backups[:-MAX_BACKUPS]:
        try:
            os.remove(old)
        except OSError:
            pass


def _load_json():
    """Load from JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return _validate_data(data)
        except (json.JSONDecodeError, IOError, ValueError):
            pass

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


def _save_json(data):
    """Save to JSON file."""
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


# ── Supabase logic ──────────────────────────────────────────────────────────

def _load_supabase():
    """Load clients from Supabase."""
    sb = _get_supabase_client()
    if not sb:
        return default_data()

    try:
        response = sb.table(TABLE_NAME).select("*").order("id").execute()
        rows = response.data if response.data else []
    except Exception:
        return default_data()

    clients = []
    for row in rows:
        clients.append({
            "id": int(row["id"]),
            "name": str(row.get("name", "")),
            "phone": str(row.get("phone", "")),
            "status": str(row.get("status", "interested")),
            "notes": row.get("notes") or [],
        })

    next_id = max((c["id"] for c in clients), default=0) + 1
    return {"next_id": next_id, "clients": clients}


def _save_supabase(data):
    """Save clients to Supabase."""
    _validate_data(data)
    sb = _get_supabase_client()
    if not sb:
        raise RuntimeError("Supabase not configured")

    try:
        # Delete all existing rows (filter: id >= 0 matches all our clients)
        sb.table(TABLE_NAME).delete().gte("id", 0).execute()

        # Bulk insert all clients
        if data["clients"]:
            rows = [
                {
                    "id": c["id"],
                    "name": c["name"],
                    "phone": c["phone"],
                    "status": c["status"],
                    "notes": c.get("notes", []),
                }
                for c in data["clients"]
            ]
            sb.table(TABLE_NAME).insert(rows).execute()
    except Exception as e:
        raise RuntimeError(f"Error saving to Supabase: {e}") from e


# ── Public API ───────────────────────────────────────────────────────────────

def load_data():
    """Load client data. Uses Supabase if configured, else JSON file."""
    if _use_supabase():
        return _load_supabase()
    return _load_json()


def save_data(data):
    """Save data. Uses Supabase if configured, else JSON file."""
    if _use_supabase():
        _save_supabase(data)
    else:
        _save_json(data)


def reorganize_ids(data):
    """Sort clients by name and renumber IDs."""
    data["clients"].sort(key=lambda c: c["name"].lower())
    for i, client in enumerate(data["clients"], 1):
        client["id"] = i
    data["next_id"] = len(data["clients"]) + 1


def find_client_by_id(clients, client_id):
    """Find a client by ID."""
    for client in clients:
        if client["id"] == client_id:
            return client
    return None
