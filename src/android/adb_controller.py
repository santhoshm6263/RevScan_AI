"""ADB Controller for Android device interaction (Spec 12 - Member 1).
Handles ADB shell commands, gestures, taps, text inputs, swipes, back navigation, app lifecycle,
and executes ActionModel instances adhering to Spec 6.3.
"""
import re
import subprocess
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from src.core.config import settings
from src.core.models import ActionModel, ElementModel


class ADBController:
    """Controls Android emulator / device via ADB."""

    def __init__(
        self,
        device_id: Optional[str] = None,
        adb_path: Optional[str] = None,
        mock_mode: Optional[bool] = None,
    ):
        self.device_id = device_id or settings.ADB_DEVICE_ID
        self.adb_path = adb_path or settings.ADB_PATH
        # If mock_mode is explicitly set, use it; otherwise auto-detect based on ADB availability
        self._mock_mode = mock_mode
        self._screen_size: Optional[Tuple[int, int]] = None

    @property
    def mock_mode(self) -> bool:
        if self._mock_mode is not None:
            return self._mock_mode
        # If no ADB device is connected and ADB cannot run, fall back gracefully to mock mode
        return not self.is_connected()

    @mock_mode.setter
    def mock_mode(self, value: bool):
        self._mock_mode = value

    def _build_command(self, cmd: List[str]) -> List[str]:
        """Builds full command list with adb binary and optional device selector."""
        base = [self.adb_path]
        if self.device_id:
            base.extend(["-s", self.device_id])
        base.extend(cmd)
        return base

    def run_cmd(self, cmd: List[str], timeout: int = 10) -> Tuple[bool, str]:
        """Executes an adb command safely with timeout handling."""
        if self._mock_mode:
            # In explicit mock mode, simulate command execution
            return True, f"[MOCK] Executed: {' '.join(cmd)}"

        full_cmd = self._build_command(cmd)
        try:
            res = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
            if res.returncode == 0:
                return True, res.stdout.strip()
            return False, res.stderr.strip()
        except FileNotFoundError:
            # ADB binary not found on PATH/filesystem
            return False, f"ADB executable not found at '{self.adb_path}'"
        except subprocess.TimeoutExpired:
            return False, f"Command timed out after {timeout}s"
        except Exception as e:
            return False, str(e)

    def is_connected(self) -> bool:
        """Check if any adb device is connected and responsive."""
        try:
            full_cmd = [self.adb_path, "devices"]
            res = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=5,
                encoding="utf-8",
                errors="replace",
            )
            if res.returncode != 0:
                return False
            # Look for lines ending with 'device' (excluding header)
            lines = [
                line.strip()
                for line in res.stdout.splitlines()[1:]
                if line.strip() and not line.startswith("*")
            ]
            active_devices = [l for l in lines if "\tdevice" in l or l.endswith("device")]
            if self.device_id:
                return any(self.device_id in d for d in active_devices)
            return len(active_devices) > 0
        except Exception:
            return False

    def get_devices(self) -> List[str]:
        """Returns a list of connected device IDs."""
        try:
            full_cmd = [self.adb_path, "devices"]
            res = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=5,
                encoding="utf-8",
                errors="replace",
            )
            if res.returncode != 0:
                return []
            devices = []
            for line in res.stdout.splitlines()[1:]:
                line = line.strip()
                if line and "\tdevice" in line:
                    devices.append(line.split("\t")[0].strip())
            return devices
        except Exception:
            return []

    def get_screen_size(self) -> Tuple[int, int]:
        """Queries the device physical or override screen resolution (width, height).
        Falls back to standard (1080, 1920) if unavailable.
        """
        if self._screen_size:
            return self._screen_size

        success, out = self.run_cmd(["shell", "wm", "size"])
        if success and out:
            # Output format: "Physical size: 1080x2400" or "Override size: 1080x2400"
            matches = re.findall(r"(\d+)x(\d+)", out)
            if matches:
                # Last match is preferred (override size overrides physical size)
                width, height = int(matches[-1][0]), int(matches[-1][1])
                self._screen_size = (width, height)
                return self._screen_size

        return 1080, 1920

    def wake_and_unlock(self) -> bool:
        """Wakes up the screen and unlocks device if locked."""
        # KEYCODE_WAKEUP = 224, KEYCODE_MENU = 82
        self.run_cmd(["shell", "input", "keyevent", "224"])
        success, _ = self.run_cmd(["shell", "input", "keyevent", "82"])
        return success

    def launch_app(self, package_name: str) -> bool:
        """Launch app by package name via monkey or am start."""
        if not package_name:
            return False
        # Monkey is the standard robust launcher when main activity name is unknown
        success, _ = self.run_cmd([
            "shell", "monkey", "-p", package_name,
            "-c", "android.intent.category.LAUNCHER", "1"
        ])
        return success

    def stop_app(self, package_name: str) -> bool:
        """Force-stops the target application package."""
        if not package_name:
            return False
        success, _ = self.run_cmd(["shell", "am", "force-stop", package_name])
        return success

    def clear_app_data(self, package_name: str) -> bool:
        """Clears application user data and cache."""
        if not package_name:
            return False
        success, _ = self.run_cmd(["shell", "pm", "clear", package_name])
        return success

    def get_current_package_and_activity(self) -> Tuple[Optional[str], Optional[str]]:
        """Returns the currently focused (package_name, activity_name)."""
        success, out = self.run_cmd(["shell", "dumpsys", "window", "windows"])
        if not success or not out:
            return None, None

        # Look for mCurrentFocus or mFocusedApp
        match = re.search(r"mCurrentFocus=Window\{[^\}]*\s+([^\/\s]+)\/([^\}\s]+)\}", out)
        if not match:
            match = re.search(r"mFocusedApp=AppWindowToken\{[^\}]*\s+([^\/\s]+)\/([^\}\s]+)\}", out)

        if match:
            return match.group(1), match.group(2)
        return None, None

    def tap(self, x: int, y: int) -> bool:
        """Tap at (x, y) coordinates."""
        success, _ = self.run_cmd(["shell", "input", "tap", str(int(x)), str(int(y))])
        return success

    def tap_bounds(self, bounds: List[int]) -> bool:
        """Calculate center point of bounds [x1, y1, x2, y2] and tap."""
        if len(bounds) != 4:
            return False
        x1, y1, x2, y2 = bounds
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        return self.tap(cx, cy)

    def type_text(self, text: str) -> bool:
        """Input text on currently focused UI element.
        Escapes special characters to ensure safe execution through ADB shell.
        """
        if not text:
            return True

        # In ADB shell input text, spaces must be encoded as %s
        # Characters like & | ; < > ( ) $ ` " ' \ ! must be properly escaped
        escaped_chars = []
        for char in text:
            if char == " ":
                escaped_chars.append("%s")
            elif char in r'&|;<>()$`"\'\!*#?[]{}':
                escaped_chars.append(f"\\{char}")
            else:
                escaped_chars.append(char)

        escaped = "".join(escaped_chars)
        success, _ = self.run_cmd(["shell", "input", "text", escaped])
        return success

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> bool:
        """Swipe between coordinates."""
        success, _ = self.run_cmd([
            "shell", "input", "swipe",
            str(int(x1)), str(int(y1)), str(int(x2)), str(int(y2)), str(duration_ms)
        ])
        return success

    def scroll(self, direction: str = "down") -> bool:
        """Perform directional scroll dynamically adapted to device screen dimensions.
        Directions: 'down', 'up', 'left', 'right'.
        """
        width, height = self.get_screen_size()
        cx = width // 2
        cy = height // 2

        if direction == "down":
            # Swipe up to scroll down
            return self.swipe(cx, int(height * 0.75), cx, int(height * 0.25), 300)
        elif direction == "up":
            # Swipe down to scroll up
            return self.swipe(cx, int(height * 0.25), cx, int(height * 0.75), 300)
        elif direction == "left":
            # Swipe right-to-left
            return self.swipe(int(width * 0.85), cy, int(width * 0.15), cy, 300)
        elif direction == "right":
            # Swipe left-to-right
            return self.swipe(int(width * 0.15), cy, int(width * 0.85), cy, 300)
        return False

    def press_back(self) -> bool:
        """Send back key event (KEYCODE_BACK = 4)."""
        success, _ = self.run_cmd(["shell", "input", "keyevent", "4"])
        return success

    def press_home(self) -> bool:
        """Send home key event (KEYCODE_HOME = 3)."""
        success, _ = self.run_cmd(["shell", "input", "keyevent", "3"])
        return success

    def press_enter(self) -> bool:
        """Send enter key event (KEYCODE_ENTER = 66)."""
        success, _ = self.run_cmd(["shell", "input", "keyevent", "66"])
        return success

    def keyevent(self, keycode: Union[int, str]) -> bool:
        """Sends an arbitrary Android key event."""
        success, _ = self.run_cmd(["shell", "input", "keyevent", str(keycode)])
        return success

    def wait(self, seconds: float = 1.0) -> bool:
        """Pauses execution for UI stability or loading."""
        time.sleep(max(0.1, seconds))
        return True

    def execute_action(
        self,
        action: Union[ActionModel, Dict[str, Any]],
        elements: Optional[List[ElementModel]] = None,
    ) -> bool:
        """Executes an action adhering strictly to Spec 6.3 Action Types:
        'tap', 'scroll', 'type', 'back', 'wait', 'finish'.

        Optional 'elements' list allows resolving target_id to bounding box coordinates.
        """
        if isinstance(action, dict):
            action_type = action.get("type", "")
            target_id = action.get("target_id")
            action_text = action.get("text")
            direction = action.get("direction", "down")
        else:
            action_type = action.type
            target_id = action.target_id
            action_text = action.text
            direction = action.direction or "down"

        # Lookup element bounds if target_id provided
        target_elem = None
        if target_id and elements:
            for elem in elements:
                if elem.id == target_id:
                    target_elem = elem
                    break

        if action_type == "tap":
            if target_elem and target_elem.bounds and any(target_elem.bounds):
                return self.tap_bounds(target_elem.bounds)
            # Fallback tap center if no target element bounds
            w, h = self.get_screen_size()
            return self.tap(w // 2, h // 2)

        elif action_type == "scroll":
            return self.scroll(direction=direction)

        elif action_type == "type":
            # If target element is specified, tap it first to gain focus
            if target_elem and target_elem.bounds and any(target_elem.bounds):
                self.tap_bounds(target_elem.bounds)
                time.sleep(0.3)
            return self.type_text(action_text or "")

        elif action_type == "back":
            return self.press_back()

        elif action_type == "wait":
            return self.wait(1.0)

        elif action_type == "finish":
            # Finish indicates end of exploration, return True
            return True

        return False


adb_controller = ADBController()
