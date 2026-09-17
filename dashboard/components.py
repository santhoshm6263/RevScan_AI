"""Shared UI components and API client for RevScan AI Dashboard (Spec 10, Spec 11 - Member 4)."""
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
        try:
            res = requests.get(f"{self.base_url}/scan/status", timeout=2)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return {"status": "idle", "step": 0, "screens_found": 0, "actions_executed": 0}

    def start_scan(self, package_name: str) -> bool:
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
        try:
            res = requests.post(f"{self.base_url}/scan/stop", timeout=3)
            return res.status_code == 200
        except Exception:
            return False

    def get_screens(self) -> List[Dict[str, Any]]:
        try:
            res = requests.get(f"{self.base_url}/screens", timeout=2)
            if res.status_code == 200:
                return res.json().get("screens", [])
        except Exception:
            pass
        return []

    def get_screen(self, screen_id: str) -> Optional[Dict[str, Any]]:
        try:
            res = requests.get(f"{self.base_url}/screens/{screen_id}", timeout=2)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return None

    def get_knowledge_pack(self) -> Dict[str, Any]:
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
