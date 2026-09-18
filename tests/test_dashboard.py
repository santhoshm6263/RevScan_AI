"""Unit tests for RevScan AI Dashboard module (Member 4)."""
import pytest
from unittest.mock import MagicMock, patch
from dashboard.components import APIClient, render_status_badge, generate_graphviz_dot


def test_api_client_default_base_url():
    """Verify APIClient initializes with default settings URL."""
    client = APIClient()
    assert client.base_url is not None
    assert "http" in client.base_url


def test_api_client_get_screenshot_url():
    """Verify screenshot path normalization and URL resolution."""
    client = APIClient("http://localhost:8000")

    # None input
    assert client.get_screenshot_url(None) is None

    # Full HTTP URL input
    assert client.get_screenshot_url("http://example.com/pic.png") == "http://example.com/pic.png"

    # Relative path input
    url = client.get_screenshot_url("screenshots/screen_001.png")
    assert url == "http://localhost:8000/screenshots/screen_001.png"

    url_data = client.get_screenshot_url("data/screenshots/screen_002.png")
    assert url_data == "http://localhost:8000/screenshots/screen_002.png"


def test_render_status_badge():
    """Verify status badge HTML formatting."""
    badge_idle = render_status_badge("idle")
    assert "badge-idle" in badge_idle
    assert "IDLE" in badge_idle

    badge_running = render_status_badge("running")
    assert "badge-running" in badge_running
    assert "RUNNING" in badge_running


def test_generate_graphviz_dot_empty():
    """Verify Graphviz DOT string generation with fallback demo graph."""
    dot = generate_graphviz_dot(transitions=[], screens=[])
    assert "digraph AppMap" in dot
    assert "Login -> Home" in dot


def test_generate_graphviz_dot_with_data():
    """Verify Graphviz DOT string generation with real screens and transitions."""
    screens = [
        {"id": "screen_001", "name": "Login Screen"},
        {"id": "screen_002", "name": "Dashboard Screen"}
    ]
    transitions = [
        {"from": "screen_001", "action": "tap:login_btn", "to": "screen_002"}
    ]
    dot = generate_graphviz_dot(transitions, screens)
    assert "digraph AppMap" in dot
    assert '"screen_001" -> "screen_002"' in dot
    assert 'label=" tap:login_btn "' in dot


@patch("requests.get")
def test_api_client_get_status_success(mock_get):
    """Verify status fetching when API call succeeds."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "running", "step": 3, "screens_found": 2, "actions_executed": 3}
    mock_get.return_value = mock_resp

    client = APIClient("http://localhost:8000")
    status = client.get_status()
    assert status["status"] == "running"
    assert status["screens_found"] == 2


@patch("requests.get")
def test_api_client_get_status_failure(mock_get):
    """Verify status fetching fallback when API is down."""
    mock_get.side_effect = Exception("Connection refused")

    client = APIClient("http://localhost:8000")
    status = client.get_status()
    assert status["status"] == "idle"
    assert status["screens_found"] == 0
