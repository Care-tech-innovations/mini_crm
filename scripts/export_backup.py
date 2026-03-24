"""
Export clients from Supabase to a JSON backup file.
Used by GitHub Actions for daily backups. Can also be run locally.

Run from project root: python scripts/export_backup.py
Environment: SUPABASE_URL and SUPABASE_KEY (from .env locally, or GitHub Secrets).
"""

import json
import os
import sys
from datetime import datetime

# Project root is parent of scripts/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Load .env for local runs
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except ImportError:
    pass

TABLE_NAME = "Ramayana's Clients"


def main():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set.", file=sys.stderr)
        return 1

    try:
        from supabase import create_client
        sb = create_client(url.strip(), key.strip())
    except Exception as e:
        print(f"Error connecting to Supabase: {e}", file=sys.stderr)
        return 1

    try:
        response = sb.table(TABLE_NAME).select("*").order("id").execute()
        rows = response.data if response.data else []
    except Exception as e:
        print(f"Error fetching from Supabase: {e}", file=sys.stderr)
        return 1

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
    data = {"next_id": next_id, "clients": clients}

    # Ensure backups dir exists
    backup_dir = os.path.join(PROJECT_ROOT, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"clientes_{timestamp}.json"
    filepath = os.path.join(backup_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Backup OK: {len(clients)} clients → {filepath}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
