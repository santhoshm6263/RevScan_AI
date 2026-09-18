"""Shared UI styles and design tokens (Spec 11 - Member 4).
Premium, high-contrast, crystal-clear typography and color palette.
Completely eliminates white-on-white text contrast issues.
"""

# Premium Design Tokens
PRIMARY = "#2563EB"
PRIMARY_HOVER = "#1D4ED8"
PRIMARY_LIGHT = "#EFF6FF"
BACKGROUND = "#F8FAFC"
SURFACE = "#FFFFFF"
SURFACE_HOVER = "#F1F5F9"
TEXT = "#0F172A"
TEXT_SECONDARY = "#334155"
MUTED = "#64748B"
SUCCESS = "#16A34A"
SUCCESS_BG = "#DCFCE7"
DANGER = "#DC2626"
DANGER_BG = "#FEE2E2"
WARNING = "#D97706"
WARNING_BG = "#FEF3C7"
BORDER = "#CBD5E1"
BORDER_LIGHT = "#E2E8F0"

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Global Reset and High-Contrast Typography */
html, body, [class*="css"], .stApp, .main {{
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: {TEXT} !important;
    background-color: {BACKGROUND} !important;
}}

/* Force all text inside Streamlit root and containers to be dark/high-contrast */
p, span, label, h1, h2, h3, h4, h5, h6, div, li, a {{
    color: {TEXT};
}}

.stMarkdown, .stMarkdown p, .stCaption, .stText {{
    color: {TEXT_SECONDARY} !important;
}}

/* Top Navigation & App Header */
.revscan-header {{
    background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
    border: 1px solid {BORDER_LIGHT};
    border-left: 5px solid {PRIMARY};
    padding: 1.25rem 1.75rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: 10px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
}}

.revscan-title {{
    font-size: 1.6rem !important;
    font-weight: 800 !important;
    color: {PRIMARY} !important;
    margin: 0 !important;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}

.revscan-subtitle {{
    font-size: 0.9rem !important;
    color: {MUTED} !important;
    margin-top: 0.25rem !important;
    font-weight: 500 !important;
}}

/* Cards & Content Panels */
.content-card {{
    background-color: {SURFACE} !important;
    border: 1px solid {BORDER_LIGHT} !important;
    border-radius: 10px !important;
    padding: 1.5rem !important;
    margin-bottom: 1.5rem !important;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.06), 0 1px 2px -1px rgba(0, 0, 0, 0.06) !important;
}}

.content-card h3, .content-card h4 {{
    color: {TEXT} !important;
    font-weight: 700 !important;
    margin-top: 0 !important;
    margin-bottom: 0.75rem !important;
}}

/* Metric Cards */
.metric-card {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER_LIGHT} !important;
    border-radius: 10px !important;
    padding: 1.25rem 1rem !important;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
    text-align: center !important;
    transition: all 0.2s ease !important;
}}

.metric-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.08) !important;
    border-color: {PRIMARY} !important;
}}

.metric-label {{
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: {MUTED} !important;
    margin-bottom: 0.4rem !important;
}}

.metric-value {{
    font-size: 2.1rem !important;
    font-weight: 800 !important;
    color: {TEXT} !important;
    line-height: 1.1 !important;
}}

/* Store App Preview Card */
.store-app-card {{
    background: {SURFACE};
    border: 1px solid {BORDER_LIGHT};
    border-radius: 10px;
    padding: 1.25rem;
    margin: 1rem 0;
    display: flex;
    align-items: center;
    gap: 1.25rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}}

.store-app-icon {{
    width: 64px;
    height: 64px;
    border-radius: 14px;
    object-fit: cover;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    background-color: {PRIMARY_LIGHT};
}}

.store-app-details {{
    flex: 1;
}}

.store-app-name {{
    font-size: 1.15rem;
    font-weight: 700;
    color: {TEXT};
    margin: 0 0 0.25rem 0;
}}

.store-app-meta {{
    font-size: 0.85rem;
    color: {MUTED};
    display: flex;
    gap: 1rem;
    align-items: center;
}}

.store-badge {{
    display: inline-block;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    background-color: {PRIMARY_LIGHT};
    color: {PRIMARY};
}}

/* Status Badges */
.badge {{
    display: inline-block;
    padding: 0.35rem 0.85rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

.badge-idle {{
    background-color: #F1F5F9;
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER};
}}

.badge-running {{
    background-color: {PRIMARY_LIGHT};
    color: {PRIMARY};
    border: 1px solid #BFDBFE;
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}}

.badge-completed {{
    background-color: {SUCCESS_BG};
    color: {SUCCESS};
    border: 1px solid #86EFAC;
}}

.badge-stopped, .badge-error {{
    background-color: {DANGER_BG};
    color: {DANGER};
    border: 1px solid #FCA5A5;
}}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: .65; }}
}}

/* Streamlit Input Fields & Widgets Explicit High-Contrast Fix */
.stTextInput > div > div > input,
input[type="text"],
.stSelectbox > div > div > div {{
    background-color: #FFFFFF !important;
    color: {TEXT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
}}

.stTextInput > div > div > input:focus {{
    border-color: {PRIMARY} !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
}}

.stTextInput label, .stSelectbox label, .stRadio label {{
    color: {TEXT} !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}}

/* Sidebar styling */
[data-testid="stSidebar"] {{
    background-color: #FFFFFF !important;
    border-right: 1px solid {BORDER_LIGHT} !important;
}}

[data-testid="stSidebar"] * {{
    color: {TEXT} !important;
}}

/* Buttons */
button[kind="primary"], .stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {PRIMARY} 0%, {PRIMARY_HOVER} 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    padding: 0.6rem 1.4rem !important;
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.25) !important;
    transition: all 0.15s ease !important;
}}

button[kind="primary"]:hover {{
    box-shadow: 0 4px 8px rgba(37, 99, 235, 0.35) !important;
    transform: translateY(-1px);
}}

button[kind="secondary"], .stButton > button {{
    background-color: #FFFFFF !important;
    color: {TEXT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}}

/* Tab Styling */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    background-color: transparent;
}}

.stTabs [data-baseweb="tab"] {{
    border-radius: 6px 6px 0 0;
    padding: 8px 16px;
    background-color: #FFFFFF;
    border: 1px solid {BORDER_LIGHT};
    color: {TEXT_SECONDARY} !important;
    font-weight: 600 !important;
}}

.stTabs [aria-selected="true"] {{
    background-color: {PRIMARY_LIGHT} !important;
    border-color: {PRIMARY} !important;
    color: {PRIMARY} !important;
}}

/* Dataframe and Table Contrast */
[data-testid="stDataFrame"], .stTable {{
    background-color: #FFFFFF !important;
    border-radius: 6px !important;
    border: 1px solid {BORDER_LIGHT} !important;
}}
</style>
"""
