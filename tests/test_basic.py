"""Basic tests verifying data models, state, and API contracts."""
import pytest
from fastapi.testclient import TestClient
from api.main import app
from src.core.models import (
    ElementModel,
    ScreenModel,
    ActionModel,
    TransitionModel,
    KnowledgePackModel
)
from src.core.state import state_manager
from src.agent.action_schema import validate_action
from src.knowledge.screen_analyzer import screen_analyzer
from src.knowledge.element_parser import element_parser

client = TestClient(app)


def test_models_instantiation():
    """Verify data models adhere strictly to Spec 6 & 7."""
    elem = ElementModel(
        id="element_001",
        type="button",
        text="Login",
        bounds=[100, 500, 900, 600],
        clickable=True,
        input=False
    )
    assert elem.id == "element_001"
    assert elem.bounds == [100, 500, 900, 600]

    action = ActionModel(type="tap", target_id="element_001")
    assert action.type == "tap"
    assert action.target_id == "element_001"

    transition = TransitionModel(**{"from": "screen_001", "action": "tap:element_001", "to": "screen_002"})
    assert transition.from_screen == "screen_001"
    assert transition.to_screen == "screen_002"

    screen = ScreenModel(
        id="screen_001",
        name="Login",
        purpose="User authentication",
        screenshot="screenshots/screen_001.png",
        elements=[elem],
        actions=[action],
        next_screens=["screen_002"]
    )
    assert screen.name == "Login"
    assert len(screen.elements) == 1

    kp = KnowledgePackModel()
    assert kp.app.name == "Demo App"
    assert kp.scan.version == "1.0"


def test_action_validation():
    """Verify action validation against allowed types."""
    valid_tap = validate_action({"type": "tap", "target_id": "btn_submit"})
    assert valid_tap is not None
    assert valid_tap.type == "tap"

    valid_scroll = validate_action({"type": "scroll"})
    assert valid_scroll is not None
    assert valid_scroll.direction == "down"

    invalid = validate_action({"type": "invalid_action"})
    assert invalid is None


def test_element_parsing_and_screen_analysis():
    """Verify element normalization and screen deduplication."""
    raw_nodes = [
        {
            "class": "android.widget.EditText",
            "resource_id": "com.example:id/email",
            "text": "Email",
            "clickable": True,
            "bounds": [100, 200, 900, 300]
        },
        {
            "class": "android.widget.Button",
            "resource_id": "com.example:id/login_btn",
            "text": "Login",
            "clickable": True,
            "bounds": [100, 400, 900, 500]
        }
    ]
    elements = element_parser.parse_elements(raw_nodes)
    assert len(elements) == 2
    assert elements[0].type == "input"
    assert elements[1].type == "button"

    screen, is_new = screen_analyzer.analyze_or_get_screen(elements)
    assert is_new is True
    assert screen.name == "Login"
    assert screen.purpose == "User authentication screen"

    # Same elements again -> deduplication check
    screen2, is_new2 = screen_analyzer.analyze_or_get_screen(elements)
    assert is_new2 is False
    assert screen2.id == screen.id


def test_api_endpoints():
    """Verify basic FastAPI endpoints match Spec 8."""
    # 1. Root
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "ready"

    # 2. GET /scan/status
    res = client.get("/scan/status")
    assert res.status_code == 200
    assert "status" in res.json()

    # 3. POST /scan/start
    res = client.post("/scan/start", json={"package_name": "com.example.test"})
    assert res.status_code == 200
    assert res.json()["status"] in ["started", "already_running"]
    assert res.json()["package_name"] == "com.example.test"

    # 4. POST /scan/stop
    res = client.post("/scan/stop")
    assert res.status_code == 200
    assert res.json()["status"] == "stopped"

    # 5. GET /screens
    res = client.get("/screens")
    assert res.status_code == 200
    assert "screens" in res.json()

    # 6. GET /knowledge-pack
    res = client.get("/knowledge-pack")
    assert res.status_code == 200
    data = res.json()
    assert "app" in data
    assert "scan" in data
    assert "design" in data


def test_orchestrator_integration():
    """Verify orchestrator autonomous exploration execution."""
    from src.core.orchestrator import orchestrator
    import time
    
    started = orchestrator.start_scan("com.example.test")
    assert started is True or orchestrator.is_running is True
    
    # Allow orchestrator to perform at least 1 step
    time.sleep(2.0)
    status = orchestrator.get_status()
    assert status.status in ["running", "completed"]
    assert status.step >= 1
    
    orchestrator.stop_scan()
    assert orchestrator.is_running is False

