"""Screenshot utility for RevScan AI (Spec 12 - Member 1).
Captures screenshots from connected device/emulator via ADB.
"""
import os
import time
from typing import Optional
from src.android.adb_controller import adb_controller
from src.core.config import settings


class ScreenshotManager:
    """Manages screenshot capture and storage."""

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or settings.SCREENSHOT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def capture_screenshot(self, filename: Optional[str] = None) -> Optional[str]:
        """Captures a screenshot from the Android device and saves locally."""
        if not filename:
            filename = f"screenshot_{int(time.time() * 1000)}.png"

        local_path = os.path.join(self.output_dir, filename)
        remote_path = "/sdcard/revscan_screenshot.png"

        # 1. Capture on device
        ok, _ = adb_controller.run_cmd(["shell", "screencap", "-p", remote_path])
        if not ok:
            return None

        # 2. Pull to local machine
        ok, _ = adb_controller.run_cmd(["pull", remote_path, local_path])
        if not ok:
            return None

        # 3. Clean up remote temp file
        adb_controller.run_cmd(["shell", "rm", remote_path])

        return local_path


screenshot_manager = ScreenshotManager()
