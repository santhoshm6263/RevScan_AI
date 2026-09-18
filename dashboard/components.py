"""Shared UI components and API client for RevScan AI Dashboard (Spec 10, Spec 11 - Member 4)."""
import os
import requests
import streamlit as st
from typing import Dict, Any, List, Optional
from src.core.config import settings
from dashboard.styles import CUSTOM_CSS, PRIMARY, MUTED, SUCCESS, DANGER, TEXT, BORDER_LIGHT


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

    def start_scan(
        self,
        package_name: str,
        platform: str = "android",
        app_name: Optional[str] = None
    ) -> bool:
        """Trigger autonomous exploration for the specified app package or store app."""
        try:
            payload = {
                "package_name": package_name,
                "platform": platform,
                "app_name": app_name
            }
            res = requests.post(
                f"{self.base_url}/scan/start",
                json=payload,
                timeout=5
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

    def resolve_app(self, query: str, platform: Optional[str] = None) -> Dict[str, Any]:
        """Resolve Google Play Store, Microsoft Store, or custom app query into metadata."""
        try:
            res = requests.post(
                f"{self.base_url}/store/resolve",
                json={"query": query, "platform": platform},
                timeout=4
            )
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        # Fallback to local resolver if API call fails
        from src.store.resolver import app_resolver
        return app_resolver.resolve(query, platform_hint=platform).model_dump()

    def get_presets(self) -> Dict[str, List[Dict[str, str]]]:
        """Fetch curated app presets."""
        try:
            res = requests.get(f"{self.base_url}/store/presets", timeout=2)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        from src.store.resolver import app_resolver
        return app_resolver.get_presets()

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


def render_header(title: str = "RevScan AI", subtitle: str = "Autonomous Android & Multi-Platform Application Explorer"):
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


def render_metric_card(label: str, value: Any):
    """Renders a high-contrast metric card."""
    html = f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_store_app_card(app_data: Dict[str, Any]):
    """Renders rich app preview card with real store metadata."""
    name = app_data.get("name", "Unknown Application")
    pkg = app_data.get("package", "")
    dev = app_data.get("developer", "Publisher")
    cat = app_data.get("category", "Application")
    platform = app_data.get("platform", "android").upper()
    rating = app_data.get("rating", 4.5)
    icon = app_data.get("icon_url") or "https://raw.githubusercontent.com/google/material-design-icons/master/png/action/android/materialicons/48dp/2x/baseline_android_black_48dp.png"
    desc = app_data.get("description", "")
    store_url = app_data.get("store_url", "")

    store_badge = f'<span class="store-badge">{platform}</span>'
    link_html = f'<a href="{store_url}" target="_blank" style="font-size:0.8rem; color:#2563EB; text-decoration:none;">View in Store ↗</a>' if store_url else ""

    html = f"""
    <div class="store-app-card">
        <img src="{icon}" class="store-app-icon" onerror="this.src='https://raw.githubusercontent.com/google/material-design-icons/master/png/action/android/materialicons/48dp/2x/baseline_android_black_48dp.png';" />
        <div class="store-app-details">
            <div class="store-app-name">{name}</div>
            <div class="store-app-meta">
                <span>{store_badge}</span>
                <span><strong>ID:</strong> <code>{pkg}</code></span>
                <span><strong>Developer:</strong> {dev}</span>
                <span><strong>Category:</strong> {cat}</span>
                <span>⭐ {rating}</span>
                {link_html}
            </div>
            <div style="font-size: 0.85rem; color: #475569; margin-top: 0.35rem;">{desc[:140]}...</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def generate_graphviz_dot(transitions: List[Dict[str, Any]], screens: List[Dict[str, Any]]) -> str:
    """Generates Graphviz DOT diagram for App Map representation."""
    dot_lines = [
        'digraph AppMap {',
        '  graph [rankdir=TB, bgcolor="transparent", fontname="Plus Jakarta Sans", pad="0.5", nodesep="0.6", ranksep="0.8"];',
        '  node [shape=rect, style="filled,rounded", fillcolor="#FFFFFF", color="#CBD5E1", penwidth=2, fontname="Plus Jakarta Sans", fontsize=11, fontcolor="#0F172A", margin="0.2,0.1"];',
        '  edge [fontname="Plus Jakarta Sans", fontsize=9, fontcolor="#475569", color="#2563EB", penwidth=1.5];'
    ]

    screen_names = {}
    for s in screens:
        sid = s.get("id")
        sname = s.get("name", sid)
        screen_names[sid] = sname

    if not transitions and not screens:
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
        for sid, sname in screen_names.items():
            node_label = f"{sname}\\n({sid})"
            dot_lines.append(f'  "{sid}" [label="{node_label}"];')

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
