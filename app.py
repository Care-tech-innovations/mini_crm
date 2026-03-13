import streamlit as st
import pandas as pd
from datetime import datetime
from data import (
    load_data,
    save_data,
    reorganize_ids,
    find_client_by_id,
    VALID_STATUSES,
)
from theme import STATUS_COLORS, MOSS, CYPRESS, OLIVE, ALOE, CEDAR, CREAM, STONE, FONT_FAMILY

st.set_page_config(page_title="Mini CRM", page_icon="\U0001f49a", layout="wide")

# Holistic design — custom CSS
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
    html, body, [class*="css"] {{
        font-family: {FONT_FAMILY};
    }}
    .stApp {{
        background-color: {CREAM};
        background-image: radial-gradient(circle at 15% 15%, {ALOE}70 0%, transparent 50%),
            radial-gradient(circle at 85% 85%, {OLIVE}60 0%, transparent 48%),
            radial-gradient(circle at 92% 8%, {MOSS}55 0%, transparent 45%),
            radial-gradient(circle at 8% 92%, {CEDAR}50 0%, transparent 42%);
    }}
    [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {{
        background: transparent !important;
        position: relative;
        z-index: 1;
    }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {CYPRESS} 0%, {MOSS} 100%);
    }}
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {{
        color: #FFFFFF !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="radio"] label {{
        color: #FFFFFF !important;
        font-weight: 500 !important;
    }}
    h1, h2, h3 {{
        color: {CYPRESS} !important;
        font-weight: 600 !important;
    }}
    .stSuccess, [data-baseweb="notification"] {{
        background-color: {ALOE} !important;
        color: {CYPRESS} !important;
        border-radius: 8px;
        border-left: 4px solid {MOSS};
    }}
    .stError {{
        background-color: #F5E6E6 !important;
        color: {CEDAR} !important;
        border-radius: 8px;
    }}
    .stWarning {{
        background-color: #F5F0E6 !important;
        color: {CEDAR} !important;
        border-radius: 8px;
    }}
    hr {{
        border-color: {CEDAR} !important;
        opacity: 0.5;
    }}
    [data-testid="stDataFrame"] {{
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(61, 79, 58, 0.08);
    }}
    .stButton > button {{
        background-color: {MOSS} !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }}
    .stButton > button:hover {{
        background-color: {CYPRESS} !important;
    }}
    .abstract-lines {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        pointer-events: none;
        z-index: 0;
        opacity: 0.18;
    }}
    </style>
    <div class="abstract-lines">
        <svg width="100%" height="100%" viewBox="0 0 1400 800" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="lineGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:{MOSS};stop-opacity:0.6"/>
                    <stop offset="100%" style="stop-color:{ALOE};stop-opacity:0.4"/>
                </linearGradient>
                <linearGradient id="lineGrad2" x1="100%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:{CEDAR};stop-opacity:0.5"/>
                    <stop offset="100%" style="stop-color:{OLIVE};stop-opacity:0.3"/>
                </linearGradient>
            </defs>
            <path fill="none" stroke="url(#lineGrad1)" stroke-width="0.8" stroke-linecap="round" d="M0 120 Q200 80 400 180 T800 100 T1200 200"/>
            <path fill="none" stroke="url(#lineGrad2)" stroke-width="0.6" stroke-linecap="round" d="M0 300 Q150 250 350 320 T700 280 T1000 350"/>
            <path fill="none" stroke="{OLIVE}" stroke-width="0.5" stroke-linecap="round" opacity="0.6" d="M100 0 Q400 100 600 50 T1100 80"/>
            <path fill="none" stroke="{CEDAR}" stroke-width="0.5" stroke-linecap="round" opacity="0.5" d="M0 450 Q300 500 600 420 T1200 480"/>
            <path fill="none" stroke="{MOSS}" stroke-width="0.4" stroke-linecap="round" opacity="0.5" d="M200 600 Q500 550 800 620 T1400 580"/>
            <path fill="none" stroke="{ALOE}" stroke-width="0.6" stroke-linecap="round" opacity="0.7" d="M-50 250 Q250 200 550 280 T950 220"/>
        </svg>
    </div>
    """,
    unsafe_allow_html=True,
)


def styled_status(status):
    color = STATUS_COLORS.get(status, "#FFFFFF")
    return f'<span style="color:{color}; font-weight:bold;">{status}</span>'


def client_selector(clients, key="client_select"):
    sorted_clients = sorted(clients, key=lambda c: c["name"].lower())
    options = [f"ID {c['id']} — {c['name']}" for c in sorted_clients]
    if not options:
        st.info("No clients available.")
        return None
    selection = st.selectbox("Select a client", options, key=key)
    selected_id = int(selection.split(" ")[1])
    return find_client_by_id(clients, selected_id)


# ── Navigation state helpers ──────────────────────────────────────────────────

if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "View all clients"

if st.session_state.get("redirect_to_all"):
    # This flag is set after adding a client; handle it BEFORE rendering sidebar.
    st.session_state["nav_page"] = "View all clients"
    st.session_state["redirect_to_all"] = False


def parse_notes_text(notes_text: str):
    """Convert the multiline Notes string back into a list of note dicts."""
    notes = []
    for line in notes_text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Expect format "YYYY-MM-DD HH:MM: text"
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


def show_clients_table(clients):
    if not clients:
        st.info("No clients to display.")
        return
    sorted_clients = sorted(clients, key=lambda c: c["name"].lower())
    df = pd.DataFrame(
        [
            {
                "ID": c["id"],
                "Name": c["name"],
                "Phone": c["phone"],
                "Status": c["status"],
                "Notes": "\n".join(
                    f"{n['date']}: {n['text']}" for n in c.get("notes", [])
                ),
            }
            for c in sorted_clients
        ]
    )

    def color_status(val):
        color = STATUS_COLORS.get(val, "#FFFFFF")
        return f"color: {color}; font-weight: bold"

    styled_df = df.style.applymap(color_status, subset=["Status"])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    st.caption(f"Total: **{len(sorted_clients)}** client(s)")


# ── Sidebar ──────────────────────────────────────────────────────────────────

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    [
        "View all clients",
        "Add client",
        "Delete client",
    ],
    key="nav_page",
)

st.sidebar.markdown("---")
st.sidebar.caption("Wellness Client Manager")


# ── Load data ────────────────────────────────────────────────────────────────

data = load_data()
clients = data["clients"]


# ── Logo (top center) ────────────────────────────────────────────────────────

col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    st.image("assets/logo_ramayana.png", use_container_width=True)
st.markdown("---")


# ── Pages ────────────────────────────────────────────────────────────────────

if page == "View all clients":
    st.title("All Clients")

    # Show "Saved" immediately at top when arriving from add/delete
    if st.session_state.get("show_saved"):
        st.success("Saved")
        st.session_state["show_saved"] = False

    if not clients:
        st.info("No clients to display.")
    else:
        # Track selected client for delete
        if "selected_client_id" not in st.session_state:
            st.session_state["selected_client_id"] = None

        # Build editable table with full notes content + Select column
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
            use_container_width=True,
            key="clients_editor",
        )

        # Update selection: only one row can be selected at a time
        selected_rows = edited_df[edited_df["Select"]]
        if len(selected_rows) >= 1:
            # Use the first selected row
            new_selected_id = int(selected_rows.iloc[0]["ID"])
            if new_selected_id != st.session_state["selected_client_id"]:
                st.session_state["selected_client_id"] = new_selected_id
                st.rerun()
        else:
            st.session_state["selected_client_id"] = None

        # Apply inline edits for Name, Phone, Status, Notes
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

        # "Saved" appears right next to the table
        if any_change:
            st.success("Saved")

        st.caption(
            "Tip: click a cell to edit. Check **Select** to choose a client for deletion."
        )

        # Selected client form + Delete button
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

elif page == "Add client":
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

elif page == "Delete client":
    st.title("Delete Client")

    if st.session_state.get("show_saved"):
        st.success("Saved")
        st.session_state["show_saved"] = False

    if not clients:
        st.info("No clients yet.")
    else:
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
                    name = client["name"]
                    data["clients"].remove(client)
                    reorganize_ids(data)
                    save_data(data)
                    st.session_state["show_saved"] = True
                    st.rerun()
