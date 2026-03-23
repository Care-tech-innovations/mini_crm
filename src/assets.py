"""
Assets: themes, styles, logo, and UI resources.
All visual design, layout, and branding in one place.
"""

import os
import streamlit as st

# Project root (parent of src/)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Theme constants ──────────────────────────────────────────────────────────

# Primary palette
MOSS = "#5A6D4C"      # Primary actions, main accents
CYPRESS = "#3D4F3A"   # Sidebar, headers, emphasis
OLIVE = "#7A8B6E"     # Secondary elements
ALOE = "#B8D4B4"      # Light backgrounds
CEDAR = "#8B7355"     # Warm accents, borders

# Neutrals
CREAM = "#F5F3EE"     # Main background
STONE = "#C4BDB2"     # Muted text, dividers

# Status colors
STATUS_COLORS = {
    "interested": OLIVE,
    "student": ALOE,
    "client": MOSS,
}

# Typography
FONT_FAMILY = "Nunito, sans-serif"

# Logo path (absolute, works locally and when deployed)
LOGO_PATH = os.path.join(_BASE_DIR, "assets", "logo_ramayana.png")


# ── Styles (CSS) ─────────────────────────────────────────────────────────────

def render_styles():
    """Inject custom CSS: background, gradients, sidebar, buttons, abstract lines."""
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


# ── Layout (Sidebar, Logo) ───────────────────────────────────────────────────

def render_sidebar():
    """Render sidebar navigation. Returns the selected page."""
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
    # Data source indicator (helps debug Supabase connection)
    try:
        from data import get_data_source
        src = get_data_source()
        if src == "supabase":
            st.sidebar.caption("✓ Datos: Supabase")
        else:
            st.sidebar.caption("⚠ Datos: archivo local — añade SUPABASE_URL y SUPABASE_KEY en Secrets")
    except Exception:
        pass
    st.sidebar.caption("Wellness Client Manager")
    return page


def render_logo():
    """Render centered logo at top of main area. Skips if file missing (e.g. deployment)."""
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        if os.path.isfile(LOGO_PATH):
            st.image(LOGO_PATH, width="stretch")
    st.markdown("---")
