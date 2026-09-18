"""Shared UI components and API client for RevScan AI Dashboard (Spec 10, Spec 11 - Member 4)."""
import os
import requests
import streamlit as st
from typing import Dict, Any, List, Optional
from src.core.config import settings
from dashboard.styles import CUSTOM_CSS, PRIMARY, MUTED, SUCCESS, DANGER


class APIClient:
    """HTTP Client connecting Streamlit frontend to FastAPI backend."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.API_BASE_URL

    def get_status(self) -> Dict[str, Any]:
        """Fetch real-time scan execution status and step counters."""
        try:
            res = requests.get(f"{self.base_url}/scan/status", timeout=2)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return {"status": "idle", "step": 0, "screens_found": 0, "actions_executed": 0}

    def start_scan(self, package_name: str) -> bool:
        """Trigger autonomous exploration for the specified app package."""
        try:
            res = requests.post(
                f"{self.base_url}/scan/start",
                json={"package_name": package_name},
                timeout=3
            )
            return res.status_code == 200
        except Exception:
            return False

    def stop_scan(self) -> bool:
        """Halt running scan execution."""
        try:
            res = requests.post(f"{self.base_url}/scan/stop", timeout=3)
            return res.status_code == 200
        except Exception:
            return False

    def get_screens(self) -> List[Dict[str, Any]]:
        """Fetch list of discovered screens summary."""
        try:
            res = requests.get(f"{self.base_url}/screens", timeout=2)
            if res.status_code == 200:
                return res.json().get("screens", [])
        except Exception:
            pass
        return []

    def get_screen(self, screen_id: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed screen information by screen ID."""
        try:
            res = requests.get(f"{self.base_url}/screens/{screen_id}", timeout=2)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return None

    def get_knowledge_pack(self) -> Dict[str, Any]:
        """Fetch the generated App Knowledge Pack JSON."""
        try:
            res = requests.get(f"{self.base_url}/knowledge-pack", timeout=3)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return {
            "app": {"name": "Demo App", "package": "com.example.demo"},
            "scan": {"version": "1.0", "screens_found": 0, "elements_found": 0, "steps": 0},
            "design": {"primary_color": "#2563EB", "background_color": "#FFFFFF", "theme": "light"},
            "screens": [],
            "journeys": [],
            "transitions": []
        }

    def get_screenshot_url(self, screenshot_path: Optional[str]) -> Optional[str]:
        """Resolves raw screenshot path to FastAPI server static endpoint or local path."""
        if not screenshot_path:
            return None
        if screenshot_path.startswith("http://") or screenshot_path.startswith("https://"):
            return screenshot_path
        # Normalize relative path (e.g. screenshots/screen_001.png -> /screenshots/screen_001.png)
        clean_path = screenshot_path.replace("\\", "/").strip("/")
        if clean_path.startswith("data/screenshots/"):
            clean_path = clean_path.replace("data/screenshots/", "")
        elif clean_path.startswith("screenshots/"):
            clean_path = clean_path.replace("screenshots/", "")
        
        url = f"{self.base_url}/screenshots/{clean_path}"
        return url


api_client = APIClient()


def inject_styles():
    """Injects custom CSS design system into Streamlit."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_header(title: str = "RevScan AI", subtitle: str = "Autonomous Android Application Explorer"):
    """Renders top header banner."""
    html = f"""
    <div class="revscan-header">
        <div>
            <div class="revscan-title">⚡ {title}</div>
            <div class="revscan-subtitle">{subtitle}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_status_badge(status: str) -> str:
    """Returns HTML for status badge."""
    css_class = f"badge badge-{status.lower()}"
    return f'<span class="{css_class}">{status.upper()}</span>'


def render_metric_card(label: str, value: Any, delta: Optional[str] = None):
    """Renders a white metric card."""
    html = f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def generate_graphviz_dot(transitions: List[Dict[str, Any]], screens: List[Dict[str, Any]]) -> str:
    """Generates Graphviz DOT diagram for App Map representation."""
    dot_lines = [
        'digraph AppMap {',
        '  graph [rankdir=TB, bgcolor="transparent", fontname="Inter", pad="0.5", nodesep="0.6", ranksep="0.8"];',
        '  node [shape=rect, style="filled,rounded", fillcolor="#FFFFFF", color="#E2E8F0", penwidth=2, fontname="Inter", fontsize=11, fontcolor="#0F172A", margin="0.2,0.1"];',
        '  edge [fontname="Inter", fontsize=9, fontcolor="#64748B", color="#2563EB", penwidth=1.5];'
    ]

    screen_names = {}
    for s in screens:
        sid = s.get("id")
        sname = s.get("name", sid)
        screen_names[sid] = sname

    if not transitions and not screens:
        # Default fallback demo graph
        dot_lines.append('  Login [fillcolor="#EFF6FF", color="#2563EB"];')
        dot_lines.append('  Home [fillcolor="#FFFFFF"];')
        dot_lines.append('  Products [fillcolor="#FFFFFF"];')
        dot_lines.append('  Details [fillcolor="#FFFFFF"];')
        dot_lines.append('  Profile [fillcolor="#FFFFFF"];')
        dot_lines.append('  Login -> Home [label="tap:login"];')
        dot_lines.append('  Home -> Products [label="tap:catalog"];')
        dot_lines.append('  Home -> Profile [label="tap:account"];')
        dot_lines.append('  Products -> Details [label="tap:item_1"];')
    else:
        # Add nodes
        for sid, sname in screen_names.items():
            node_label = f"{sname}\\n({sid})"
            dot_lines.append(f'  "{sid}" [label="{node_label}"];')

        # Add edges
        for t in transitions:
            from_s = t.get("from", "Unknown")
            action = t.get("action", "action")
            to_s = t.get("to", "Unknown")
            if from_s not in screen_names:
                dot_lines.append(f'  "{from_s}" [label="{from_s}"];')
            if to_s not in screen_names:
                dot_lines.append(f'  "{to_s}" [label="{to_s}"];')
            dot_lines.append(f'  "{from_s}" -> "{to_s}" [label=" {action} "];')

    dot_lines.append('}')
    return "\n".join(dot_lines)

