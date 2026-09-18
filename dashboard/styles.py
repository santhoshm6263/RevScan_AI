"""Shared UI styles and design tokens (Spec 11 - Member 4).
Adheres strictly to the color palette and typography specified in PROJECT_SPEC.md.
"""

# Design Tokens (Spec 11)
PRIMARY = "#2563EB"
BACKGROUND = "#F8FAFC"
SURFACE = "#FFFFFF"
TEXT = "#0F172A"
MUTED = "#64748B"
SUCCESS = "#16A34A"
DANGER = "#DC2626"
BORDER = "#E2E8F0"

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: {TEXT};
    background-color: {BACKGROUND};
}}

.stApp {{
    background-color: {BACKGROUND};
}}

/* Top Header Bar */
.revscan-header {{
    background-color: {SURFACE};
    border-bottom: 1px solid {BORDER};
    padding: 1.25rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}}

.revscan-title {{
    font-size: 1.5rem;
    font-weight: 700;
    color: {PRIMARY};
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}

.revscan-subtitle {{
    font-size: 0.875rem;
    color: {MUTED};
    margin-top: 0.25rem;
}}

/* Metric Card */
.metric-card {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 1.25rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    text-align: center;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}

.metric-card:hover {{
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
}}

.metric-label {{
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: {MUTED};
    margin-bottom: 0.5rem;
}}

.metric-value {{
    font-size: 2rem;
    font-weight: 700;
    color: {TEXT};
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
    color: {MUTED};
    border: 1px solid {BORDER};
}}

.badge-running {{
    background-color: #EFF6FF;
    color: {PRIMARY};
    border: 1px solid #BFDBFE;
}}

.badge-completed {{
    background-color: #ECFDF5;
    color: {SUCCESS};
    border: 1px solid #A7F3D0;
}}

.badge-stopped {{
    background-color: #FEF2F2;
    color: {DANGER};
    border: 1px solid #FECACA;
}}

.badge-error {{
    background-color: #FEF2F2;
    color: {DANGER};
    border: 1px solid #FECACA;
}}

/* Content Card */
.content-card {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}}

.content-card h3 {{
    margin-top: 0;
    margin-bottom: 1rem;
    font-size: 1.15rem;
    font-weight: 600;
    color: {TEXT};
}}

/* Graph Container */
.graph-container {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 1.5rem;
    text-align: center;
    overflow-x: auto;
}}

/* Button styling override */
button[kind="primary"] {{
    background-color: {PRIMARY} !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.25rem !important;
}}

button[kind="secondary"] {{
    background-color: {SURFACE} !important;
    color: {TEXT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
}}

/* Screen list item */
.screen-list-item {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    cursor: pointer;
}}
</style>
"""

