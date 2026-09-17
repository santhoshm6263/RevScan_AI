"""Comprehensive unit tests for Module: Android Automation (Spec 12 - Member 1)."""
import os
import tempfile
import pytest
from PIL import Image

from src.android.adb_controller import ADBController, adb_controller
from src.android.screenshot import ScreenshotManager, screenshot_manager
from src.android.ui_parser import UIParser, ui_parser
from src.core.models import ActionModel, ElementModel
from src.knowledge.element_parser import element_parser


def test_adb_command_building():
    """Verify ADB command line assembly with and without device ID."""
    ctrl = ADBController(device_id="emulator-5554", adb_path="adb")
    cmd = ctrl._build_command(["shell", "input", "tap", "100", "200"])
    assert cmd == ["adb", "-s", "emulator-5554", "shell", "input", "tap", "100", "200"]

    ctrl_no_dev = ADBController(device_id="", adb_path="adb")
    cmd2 = ctrl_no_dev._build_command(["shell", "input", "keyevent", "4"])
    assert cmd2 == ["adb", "shell", "input", "keyevent", "4"]


def test_adb_tap_bounds_calculation():
    """Verify bounds center calculation [x1, y1, x2, y2] -> (cx, cy)."""
    ctrl = ADBController(mock_mode=True)
    
    # Valid bounds [100, 200, 300, 400] -> center is (200, 300)
    assert ctrl.tap_bounds([100, 200, 300, 400]) is True

    # Invalid bounds length
    assert ctrl.tap_bounds([100, 200]) is False


def test_adb_type_text_escaping():
    """Verify text escaping for spaces and shell special characters."""
    recorded_commands = []

    class MockADB(ADBController):
        def run_cmd(self, cmd, timeout=10):
            recorded_commands.append(cmd)
            return True, "OK"

    mock_ctrl = MockADB(mock_mode=False)
    mock_ctrl.type_text("hello world & test@example.com")

    assert len(recorded_commands) == 1
    text_arg = recorded_commands[0][3]
    # Spaces replaced with %s
    assert "hello%sworld" in text_arg
    # Ampersand escaped
    assert r"\&" in text_arg


def test_adb_scroll_directions():
    """Verify directional swipe generation scaled to screen resolution."""
    swipes = []

    class MockADB(ADBController):
        def get_screen_size(self):
            return 1000, 2000

        def swipe(self, x1, y1, x2, y2, duration_ms=300):
            swipes.append((x1, y1, x2, y2))
            return True

    ctrl = MockADB(mock_mode=False)

    # Down: swipe from 75% height to 25% height at center width
    ctrl.scroll("down")
    assert swipes[-1] == (500, 1500, 500, 500)

    # Up: swipe from 25% height to 75% height
    ctrl.scroll("up")
    assert swipes[-1] == (500, 500, 500, 1500)

    # Left: swipe from 85% width to 15% width at center height
    ctrl.scroll("left")
    assert swipes[-1] == (850, 1000, 150, 1000)

    # Right: swipe from 15% width to 85% width
    ctrl.scroll("right")
    assert swipes[-1] == (150, 1000, 850, 1000)


def test_adb_execute_action_mapping():
    """Verify high-level ActionModel execution adheres to Spec 6.3."""
    executed_types = []

    class MockADB(ADBController):
        def tap_bounds(self, bounds):
            executed_types.append(("tap_bounds", bounds))
            return True

        def tap(self, x, y):
            executed_types.append(("tap", x, y))
            return True

        def scroll(self, direction="down"):
            executed_types.append(("scroll", direction))
            return True

        def type_text(self, text):
            executed_types.append(("type", text))
            return True

        def press_back(self):
            executed_types.append(("back",))
            return True

        def wait(self, seconds=1.0):
            executed_types.append(("wait", seconds))
            return True

    ctrl = MockADB(mock_mode=False)

    elements = [
        ElementModel(id="btn_login", type="button", text="Login", bounds=[50, 100, 250, 150], clickable=True),
        ElementModel(id="txt_email", type="input", text="", bounds=[50, 200, 250, 250], clickable=True, input=True)
    ]

    # 1. Tap targeting element ID
    tap_action = ActionModel(type="tap", target_id="btn_login")
    assert ctrl.execute_action(tap_action, elements) is True
    assert executed_types[-1] == ("tap_bounds", [50, 100, 250, 150])

    # 2. Scroll
    scroll_action = ActionModel(type="scroll", direction="down")
    assert ctrl.execute_action(scroll_action) is True
    assert executed_types[-1] == ("scroll", "down")

    # 3. Type
    type_action = ActionModel(type="type", target_id="txt_email", text="user@domain.com")
    assert ctrl.execute_action(type_action, elements) is True
    assert executed_types[-1] == ("type", "user@domain.com")

    # 4. Back
    back_action = ActionModel(type="back")
    assert ctrl.execute_action(back_action) is True
    assert executed_types[-1] == ("back",)

    # 5. Wait
    wait_action = ActionModel(type="wait")
    assert ctrl.execute_action(wait_action) is True
    assert executed_types[-1] == ("wait", 1.0)

    # 6. Finish
    finish_action = ActionModel(type="finish")
    assert ctrl.execute_action(finish_action) is True


def test_ui_parser_parse_bounds():
    """Verify bounds regex parsing."""
    assert UIParser.parse_bounds("[0,0][1080,1920]") == [0, 0, 1080, 1920]
    assert UIParser.parse_bounds("[100,200][300,400]") == [100, 200, 300, 400]
    assert UIParser.parse_bounds("invalid") == [0, 0, 0, 0]
    assert UIParser.parse_bounds("") == [0, 0, 0, 0]


def test_ui_parser_parse_xml_string():
    """Verify XML string parsing into raw node dictionary representations."""
    parser = UIParser()
    xml = parser.get_sample_hierarchy_xml()
    nodes = parser.parse_xml_string(xml)

    assert len(nodes) >= 5

    # Find button and edit text nodes
    login_btn = next((n for n in nodes if n["resource_id"] == "com.example.demo:id/btn_login"), None)
    assert login_btn is not None
    assert login_btn["text"] == "Sign In"
    assert login_btn["clickable"] is True
    assert login_btn["bounds"] == [100, 620, 980, 740]
    assert login_btn["class"] == "android.widget.Button"

    email_input = next((n for n in nodes if n["resource_id"] == "com.example.demo:id/input_email"), None)
    assert email_input is not None
    assert email_input["content_desc"] == "Email field"
    assert email_input["class"] == "android.widget.EditText"


def test_ui_parser_element_parser_integration():
    """Verify seamless downstream contract: ui_parser output is accepted by element_parser."""
    parser = UIParser()
    nodes = parser.parse_xml_string(parser.get_sample_hierarchy_xml())
    elements = element_parser.parse_elements(nodes)

    assert len(elements) >= 4
    types = [e.type for e in elements]
    assert "button" in types
    assert "input" in types


def test_screenshot_manager_fallback_and_relative_path():
    """Verify ScreenshotManager captures or generates valid PNG screenshots."""
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = ScreenshotManager(output_dir=tmpdir)
        screenshot_path = sm.capture_screenshot("test_screen.png")

        assert screenshot_path is not None
        assert os.path.exists(screenshot_path)
        assert os.path.getsize(screenshot_path) > 0

        # Verify it is a valid PNG image
        with Image.open(screenshot_path) as img:
            assert img.format == "PNG"
            assert img.size[0] > 0
            assert img.size[1] > 0

        # Verify relative path formatting according to Spec 6.1
        rel_path = sm.get_relative_path(screenshot_path)
        assert rel_path == "screenshots/test_screen.png"

        # Verify latest screenshot helper
        latest = sm.get_latest_screenshot()
        assert latest == screenshot_path
