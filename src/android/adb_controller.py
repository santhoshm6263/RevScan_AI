"""ADB Controller for Android device interaction (Spec 12 - Member 1).
Handles ADB shell commands, taps, text inputs, swipes, back button, and app launch.
"""
import subprocess
from typing import List, Optional, Tuple
from src.core.config import settings


class ADBController:
    """Controls Android emulator / device via ADB."""

    def __init__(self, device_id: Optional[str] = None, adb_path: Optional[str] = None):
        self.device_id = device_id or settings.ADB_DEVICE_ID
        self.adb_path = adb_path or settings.ADB_PATH

    def _build_command(self, cmd: List[str]) -> List[str]:
        base = [self.adb_path]
        if self.device_id:
            base.extend(["-s", self.device_id])
        base.extend(cmd)
        return base

    def run_cmd(self, cmd: List[str], timeout: int = 10) -> Tuple[bool, str]:
        """Executes an adb command."""
        full_cmd = self._build_command(cmd)
        try:
            res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout)
            if res.returncode == 0:
                return True, res.stdout.strip()
            return False, res.stderr.strip()
        except Exception as e:
            return False, str(e)

    def is_connected(self) -> bool:
        """Check if any adb device is connected."""
        success, out = self.run_cmd(["devices"])
        if not success:
            return False
        lines = [line for line in out.splitlines()[1:] if line.strip() and "device" in line]
        return len(lines) > 0

    def launch_app(self, package_name: str) -> bool:
        """Launch app by package name via monkey or am start."""
        success, _ = self.run_cmd([
            "shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"
        ])
        return success

    def tap(self, x: int, y: int) -> bool:
        """Tap at (x, y) coordinates."""
        success, _ = self.run_cmd(["shell", "input", "tap", str(x), str(y)])
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
        """Input text on current focused element."""
        # Replace spaces for adb input compatibility
        escaped = text.replace(" ", "%s")
        success, _ = self.run_cmd(["shell", "input", "text", escaped])
        return success

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> bool:
        """Swipe between coordinates."""
        success, _ = self.run_cmd(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)])
        return success

    def scroll(self, direction: str = "down") -> bool:
        """Perform a standard directional scroll."""
        if direction == "down":
            return self.swipe(500, 1400, 500, 600)
        elif direction == "up":
            return self.swipe(500, 600, 500, 1400)
        elif direction == "left":
            return self.swipe(800, 1000, 200, 1000)
        elif direction == "right":
            return self.swipe(200, 1000, 800, 1000)
        return False

    def press_back(self) -> bool:
        """Send back key event (KEYCODE_BACK = 4)."""
        success, _ = self.run_cmd(["shell", "input", "keyevent", "4"])
        return success


adb_controller = ADBController()
