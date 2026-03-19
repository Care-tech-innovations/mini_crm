"""
Client Management: all functionality for managing clients.
Includes view_all_clients, add_client, delete_client and their helpers.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from data import (
    save_data,
    reorganize_ids,
    find_client_by_id,
    VALID_STATUSES,
)
from assets import STATUS_COLORS


def parse_notes_text(notes_text: str):
    """Convert the multiline Notes string back into a list of note dicts."""
    notes = []
    for line in notes_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if len(line) > 18 and line[16:18] == ": ":
            date_part = line[:16]
            text_part = line[18:]
            notes.append({"date": date_part, "text": text_part})
        else:
            notes.append(
                {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "text": line,
                }
            )
    return notes


def client_selector(clients, key="client_select"):
    """Show selectbox to choose a client. Returns selected client or None."""
    sorted_clients = sorted(clients, key=lambda c: c["name"].lower())
    options = [f"ID {c['id']} — {c['name']}" for c in sorted_clients]
    if not options:
        st.info("No clients available.")
        return None
    selection = st.selectbox("Select a client", options, key=key)
    selected_id = int(selection.split(" ")[1])
    return find_client_by_id(clients, selected_id)


def styled_status(status):
    """Return HTML for colored status display."""
    color = STATUS_COLORS.get(status, "#FFFFFF")
    return f'<span style="color:{color}; font-weight:bold;">{status}</span>'


def view_all_clients(clients, data):
    """View all clients with editable table, inline edits, and delete."""
    st.title("All Clients")

    if st.session_state.get("show_saved"):
        st.success("Saved")
        st.session_state["show_saved"] = False

    if not clients:
        st.info("No clients to display.")
        return

    if "selected_client_id" not in st.session_state:
        st.session_state["selected_client_id"] = None

    sorted_clients = sorted(clients, key=lambda c: c["name"].lower())
    rows = []
    for c in sorted_clients:
        notes_text = "\n".join(
            f"{n['date']}: {n['text']}" for n in c.get("notes", [])
        )
        is_selected = st.session_state["selected_client_id"] == c["id"]
        rows.append(
            {
                "Select": is_selected,
                "ID": c["id"],
                "Name": c["name"],
                "Phone": c["phone"],
                "Status": c["status"],
                "Notes": notes_text,
            }
        )

    df = pd.DataFrame(rows)

    edited_df = st.data_editor(
        df,
        column_config={
            "Select": st.column_config.CheckboxColumn(
                "Select",
                help="Check to select this client for deletion",
                required=False,
            ),
            "ID": st.column_config.NumberColumn(disabled=True),
            "Phone": st.column_config.TextColumn(),
            "Notes": st.column_config.TextColumn(),
            "Status": st.column_config.SelectboxColumn(
                options=VALID_STATUSES
            ),
        },
        hide_index=True,
        width="stretch",
        key="clients_editor",
    )

    selected_rows = edited_df[edited_df["Select"]]
    if len(selected_rows) >= 1:
        new_selected_id = int(selected_rows.iloc[0]["ID"])
        if new_selected_id != st.session_state["selected_client_id"]:
            st.session_state["selected_client_id"] = new_selected_id
            st.rerun()
    else:
        st.session_state["selected_client_id"] = None

    id_to_client = {c["id"]: c for c in clients}
    any_change = False
    name_changed = False

    for _, row in edited_df.iterrows():
        client_id = int(row["ID"])
        client = id_to_client.get(client_id)
        if not client:
            continue

        new_name = str(row["Name"]).strip()
        new_status = str(row["Status"]).strip()
        new_phone = str(row["Phone"]).strip()
        new_notes_raw = str(row["Notes"]).strip()

        if new_name and new_name != client["name"]:
            client["name"] = new_name
            any_change = True
            name_changed = True

        if (
            new_status
            and new_status in VALID_STATUSES
            and new_status != client["status"]
        ):
            client["status"] = new_status
            any_change = True

        if new_phone and new_phone != client["phone"]:
            client["phone"] = new_phone
            any_change = True

        original_notes_text = "\n".join(
            f"{n['date']}: {n['text']}" for n in client.get("notes", [])
        )
        if new_notes_raw != original_notes_text:
            client["notes"] = parse_notes_text(new_notes_raw)
            any_change = True

    if any_change:
        if name_changed:
            reorganize_ids(data)
        save_data(data)

    if any_change:
        st.success("Saved")

    st.caption(
        "Tip: click a cell to edit. Check **Select** to choose a client for deletion."
    )

    selected_id = st.session_state["selected_client_id"]
    selected_client = find_client_by_id(clients, selected_id) if selected_id else None

    if selected_client:
        st.markdown("---")
        st.subheader("Selected client")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.text_input("Name", value=selected_client["name"], disabled=True, key="disp_name")
        with col2:
            st.text_input("Phone", value=selected_client["phone"], disabled=True, key="disp_phone")
        with col3:
            st.selectbox(
                "Status",
                VALID_STATUSES,
                index=VALID_STATUSES.index(selected_client["status"])
                if selected_client["status"] in VALID_STATUSES
                else 0,
                disabled=True,
                key="disp_status",
            )
        with col4:
            if st.button("Delete Client", type="primary", key="delete_from_list"):
                data["clients"].remove(selected_client)
                reorganize_ids(data)
                save_data(data)
                st.session_state["selected_client_id"] = None
                st.session_state["show_saved"] = True
                st.rerun()

        if selected_client.get("notes"):
            st.text_area(
                "Notes",
                value="\n".join(
                    f"{n['date']}: {n['text']}" for n in selected_client["notes"]
                ),
                disabled=True,
                height=100,
                key="disp_notes",
            )


def add_client(clients, data):
    """Add a new client via form."""
    st.title("Add New Client")

    with st.form("add_client_form", clear_on_submit=True):
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        submitted = st.form_submit_button("Add client")

    if submitted:
        name_val = (name or "").strip()
        phone_val = (phone or "").strip()
        if not name_val or not phone_val:
            st.error("Name and phone cannot be empty.")
        else:
            try:
                clients.append({
                    "id": 0,
                    "name": name_val,
                    "phone": phone_val,
                    "status": "interested",
                    "notes": [],
                })
                reorganize_ids(data)
                save_data(data)
                st.session_state["show_saved"] = True
                st.session_state["redirect_to_all"] = True
                st.rerun()
            except Exception as e:
                st.error(f"Error adding client: {e}")


def delete_client(clients, data):
    """Delete a client with confirmation."""
    st.title("Delete Client")

    if st.session_state.get("show_saved"):
        st.success("Saved")
        st.session_state["show_saved"] = False

    if not clients:
        st.info("No clients yet.")
        return

    client = client_selector(clients, key="delete_select")
    if client:
        st.warning(
            f"You are about to delete **{client['name']}** "
            f"(Phone: {client['phone']}, Status: {client['status']})."
        )
        confirm = st.checkbox("I am sure I want to delete this client")

        if st.button("Delete client"):
            if not confirm:
                st.error("Please check the confirmation box first.")
            else:
                data["clients"].remove(client)
                reorganize_ids(data)
                save_data(data)
                st.session_state["show_saved"] = True
                st.rerun()
