import json
import os
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "clients.json")

VALID_STATUSES = ["interested", "student", "client"]

STATUS_COLORS = {
    "interested": Fore.LIGHTYELLOW_EX,
    "student": Fore.LIGHTCYAN_EX,
    "client": Fore.LIGHTGREEN_EX,
}

G = Fore.LIGHTGREEN_EX
B = Fore.LIGHTCYAN_EX
W = Fore.WHITE
R = Fore.LIGHTRED_EX
DIM = Style.DIM
BOLD = Style.BRIGHT
RESET = Style.RESET_ALL


def default_data():
    return {"next_id": 1, "clients": []}


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return default_data()


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


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


def colored_status(status):
    color = STATUS_COLORS.get(status, W)
    return f"{color}{status:<11}{RESET}"


def add_client(data):
    print(f"\n{B}{BOLD}--- Add New Client ---{RESET}")

    name = input(f"{W}Name: {RESET}").strip()
    if not name:
        print(f"{R}[!] Name cannot be empty.{RESET}")
        return

    phone = input(f"{W}Phone: {RESET}").strip()
    if not phone:
        print(f"{R}[!] Phone cannot be empty.{RESET}")
        return

    client = {
        "id": 0,
        "name": name,
        "phone": phone,
        "status": "interested",
        "notes": []
    }

    data["clients"].append(client)
    reorganize_ids(data)
    save_data(data)
    print(f"{G}[+] Client added: {name} (ID: {client['id']}){RESET}")


def view_clients(clients):
    if not clients:
        print(f"\n{W}No clients found.{RESET}")
        return

    sorted_clients = sorted(clients, key=lambda c: c["name"].lower())

    border = f"{G}+----+----------------------------------+----------------+------------+{RESET}"
    print(f"\n{border}")
    print(f"{G}|{RESET}{BOLD} {'ID':<3}{RESET}{G}|{RESET}{BOLD} {'Name':<33}{RESET}{G}|{RESET}{BOLD} {'Phone':<15}{RESET}{G}|{RESET}{BOLD} {'Status':<11}{RESET}{G}|{RESET}")
    print(border)

    for c in sorted_clients:
        status_display = colored_status(c["status"])
        print(f"{G}|{RESET} {W}{c['id']:<3}{RESET}{G}|{RESET} {W}{c['name']:<33}{RESET}{G}|{RESET} {W}{c['phone']:<15}{RESET}{G}|{RESET} {status_display}{G}|{RESET}")

    print(border)
    print(f"{W}Total: {BOLD}{len(sorted_clients)}{RESET}{W} client(s){RESET}")


def change_status(data):
    print(f"\n{B}{BOLD}--- Change Client Status ---{RESET}")
    view_clients(data["clients"])

    if not data["clients"]:
        return

    try:
        client_id = int(input(f"\n{W}Enter client ID: {RESET}"))
    except ValueError:
        print(f"{R}[!] Invalid ID. Please enter a number.{RESET}")
        return

    client = find_client_by_id(data["clients"], client_id)
    if not client:
        print(f"{R}[!] No client found with ID {client_id}.{RESET}")
        return

    current_color = STATUS_COLORS.get(client["status"], W)
    print(f"\n{W}{client['name']} — current status: {current_color}{client['status']}{RESET}")
    print(f"{W}Pick new status:{RESET}")
    for i, status in enumerate(VALID_STATUSES, 1):
        color = STATUS_COLORS.get(status, W)
        print(f"  {W}{i}. {color}{status}{RESET}")

    try:
        choice = int(input(f"{W}Option: {RESET}"))
    except ValueError:
        print(f"{R}[!] Invalid option.{RESET}")
        return

    if choice < 1 or choice > len(VALID_STATUSES):
        print(f"{R}[!] Invalid option.{RESET}")
        return

    new_status = VALID_STATUSES[choice - 1]
    client["status"] = new_status
    save_data(data)
    new_color = STATUS_COLORS.get(new_status, W)
    print(f"{G}[+] {client['name']} status changed to: {new_color}{new_status}{RESET}")


def add_note(data):
    print(f"\n{B}{BOLD}--- Add Note to Client ---{RESET}")
    view_clients(data["clients"])

    if not data["clients"]:
        return

    try:
        client_id = int(input(f"\n{W}Enter client ID: {RESET}"))
    except ValueError:
        print(f"{R}[!] Invalid ID. Please enter a number.{RESET}")
        return

    client = find_client_by_id(data["clients"], client_id)
    if not client:
        print(f"{R}[!] No client found with ID {client_id}.{RESET}")
        return

    if client["notes"]:
        print(f"\n{B}{BOLD}--- Notes for {client['name']} ---{RESET}")
        for note in client["notes"]:
            print(f"  {DIM}{note['date']}{RESET} {W}{note['text']}{RESET}")
    else:
        print(f"\n{W}{client['name']} has no notes yet.{RESET}")

    text = input(f"\n{W}Write your note: {RESET}").strip()
    if not text:
        print(f"{R}[!] Note cannot be empty.{RESET}")
        return

    note = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "text": text
    }

    client["notes"].append(note)
    save_data(data)
    print(f"{G}[+] Note added to {client['name']}.{RESET}")


def edit_client(data):
    print(f"\n{B}{BOLD}--- Edit Client Info ---{RESET}")
    view_clients(data["clients"])

    if not data["clients"]:
        return

    try:
        client_id = int(input(f"\n{W}Enter client ID: {RESET}"))
    except ValueError:
        print(f"{R}[!] Invalid ID. Please enter a number.{RESET}")
        return

    client = find_client_by_id(data["clients"], client_id)
    if not client:
        print(f"{R}[!] No client found with ID {client_id}.{RESET}")
        return

    print(f"\n{W}Editing: {BOLD}{client['name']}{RESET}")
    print(f"{W}What do you want to edit?{RESET}")
    print(f"  {W}1. {B}Name{RESET}")
    print(f"  {W}2. {B}Phone{RESET}")

    try:
        choice = int(input(f"{W}Option: {RESET}"))
    except ValueError:
        print(f"{R}[!] Invalid option.{RESET}")
        return

    if choice == 1:
        print(f"{W}Current name: {BOLD}{client['name']}{RESET}")
        new_name = input(f"{W}New name: {RESET}").strip()
        if not new_name:
            print(f"{R}[!] Name cannot be empty.{RESET}")
            return
        client["name"] = new_name
        reorganize_ids(data)
        save_data(data)
        print(f"{G}[+] Name updated to: {new_name}{RESET}")
    elif choice == 2:
        print(f"{W}Current phone: {BOLD}{client['phone']}{RESET}")
        new_phone = input(f"{W}New phone: {RESET}").strip()
        if not new_phone:
            print(f"{R}[!] Phone cannot be empty.{RESET}")
            return
        client["phone"] = new_phone
        save_data(data)
        print(f"{G}[+] Phone updated to: {new_phone}{RESET}")
    else:
        print(f"{R}[!] Invalid option.{RESET}")


def delete_client(data):
    print(f"\n{R}{BOLD}--- Delete Client ---{RESET}")
    view_clients(data["clients"])

    if not data["clients"]:
        return

    try:
        client_id = int(input(f"\n{W}Enter client ID: {RESET}"))
    except ValueError:
        print(f"{R}[!] Invalid ID. Please enter a number.{RESET}")
        return

    client = find_client_by_id(data["clients"], client_id)
    if not client:
        print(f"{R}[!] No client found with ID {client_id}.{RESET}")
        return

    confirm = input(f"{R}Are you sure you want to delete {BOLD}{client['name']}{RESET}{R}? (y/n): {RESET}").strip().lower()
    if confirm == "y":
        data["clients"].remove(client)
        reorganize_ids(data)
        save_data(data)
        print(f"{G}[+] Client deleted: {client['name']}{RESET}")
    else:
        print(f"{W}Cancelled. No client was deleted.{RESET}")


def search_by_status(data):
    print(f"\n{B}{BOLD}--- Search by Status ---{RESET}")
    print(f"{W}Pick a status to search:{RESET}")
    for i, status in enumerate(VALID_STATUSES, 1):
        color = STATUS_COLORS.get(status, W)
        print(f"  {W}{i}. {color}{status}{RESET}")

    try:
        choice = int(input(f"{W}Option: {RESET}"))
    except ValueError:
        print(f"{R}[!] Invalid option.{RESET}")
        return

    if choice < 1 or choice > len(VALID_STATUSES):
        print(f"{R}[!] Invalid option.{RESET}")
        return

    status = VALID_STATUSES[choice - 1]
    results = [c for c in data["clients"] if c["status"] == status]

    color = STATUS_COLORS.get(status, W)
    print(f"\n{W}Clients with status: {color}{status}{RESET}")
    view_clients(results)


def main():
    data = load_data()
    reorganize_ids(data)
    save_data(data)

    while True:
        os.system("cls")
        print(f"{G}{BOLD}========= MINI CRM ========={RESET}")
        print(f"  {W}1. {G}Add client{RESET}")
        print(f"  {W}2. {B}View all clients{RESET}")
        print(f"  {W}3. {B}Change client status{RESET}")
        print(f"  {W}4. {B}Add note to client{RESET}")
        print(f"  {W}5. {B}Search by status{RESET}")
        print(f"  {W}6. {B}Edit client info{RESET}")
        print(f"  {W}7. {R}Delete client{RESET}")
        print(f"  {W}8. {R}Exit{RESET}")
        print(f"{G}{BOLD}============================={RESET}")

        option = input(f"{W}Choose an option: {RESET}").strip()

        if option == "1":
            add_client(data)
        elif option == "2":
            view_clients(data["clients"])
        elif option == "3":
            change_status(data)
        elif option == "4":
            add_note(data)
        elif option == "5":
            search_by_status(data)
        elif option == "6":
            edit_client(data)
        elif option == "7":
            delete_client(data)
        elif option == "8":
            print(f"\n{G}Goodbye! Your data has been saved.{RESET}")
            break
        else:
            print(f"\n{R}[!] Invalid option. Please choose 1-8.{RESET}")

        input(f"\n{DIM}Press Enter to continue...{RESET}")


if __name__ == "__main__":
    main()
