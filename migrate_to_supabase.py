"""
One-time script to migrate clients from clients.json to Supabase.
Run from project root: python migrate_to_supabase.py
Uses Supabase REST API (no supabase package required).
"""

import json
import os
import urllib.request
import urllib.error
from urllib.parse import quote

# Load .env from project root
try:
    from dotenv import load_dotenv
    script_dir = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(script_dir, ".env"))
except ImportError:
    script_dir = os.path.dirname(os.path.abspath(__file__))

def main():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return 1

    json_path = os.path.join(script_dir, "clients.json")
    if not os.path.exists(json_path):
        print("Error: clients.json not found.")
        return 1

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    clients = data.get("clients", [])
    if not clients:
        print("No clients to migrate.")
        return 0

    base = url.rstrip("/")
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    # Table name - use "Ramayana's Clients" if that's what you created in Supabase
    table_name = os.environ.get("SUPABASE_TABLE", "Ramayana's Clients")
    table_encoded = quote(table_name, safe="")

    print(f"Migrating {len(clients)} clients to Supabase (table: {table_name})...")
    try:
        # Delete existing rows (id >= 0)
        req = urllib.request.Request(
            f"{base}/rest/v1/{table_encoded}?id=gte.0",
            method="DELETE",
            headers=headers,
        )
        urllib.request.urlopen(req)

        # Insert clients one by one (bulk insert via POST)
        rows = [
            {
                "id": c["id"],
                "name": c["name"],
                "phone": c["phone"],
                "status": c["status"],
                "notes": c.get("notes", []),
            }
            for c in clients
        ]
        body = json.dumps(rows).encode("utf-8")
        req = urllib.request.Request(
            f"{base}/rest/v1/{table_encoded}",
            data=body,
            method="POST",
            headers={**headers, "Content-Length": str(len(body))},
        )
        urllib.request.urlopen(req)
        print("Done! Your clients are now in Supabase.")
        return 0
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"Error: {e.code} {e.reason}")
        print(body)
        if "row-level security" in body.lower() or "42501" in body:
            print("\n→ Fix: In Supabase, go to Authentication → Policies.")
            print("  Add a policy for table \"Ramayana's Clients\" to allow anon ALL operations.")
            print("  Or run in SQL Editor: ALTER TABLE \"Ramayana's Clients\" DISABLE ROW LEVEL SECURITY;")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
