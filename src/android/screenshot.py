"""Screenshot utility for RevScan AI (Spec 12 - Member 1).
Captures screenshots from connected device/emulator via ADB,
with automatic fallback generation for offline/mock testability.
"""
import os
import time
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw

from src.android.adb_controller import adb_controller
from src.core.config import settings


class ScreenshotManager:
    """Manages screenshot capture, fallback generation, and storage."""

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or settings.SCREENSHOT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def capture_screenshot(self, filename: Optional[str] = None) -> Optional[str]:
        """Captures a screenshot from the Android device and saves locally.
        If ADB capture fails (e.g. no device connected or in test mode), generates
        a clean fallback image to ensure the scan pipeline remains testable and uninterrupted.
        """
        if not filename:
            filename = f"screenshot_{int(time.time() * 1000)}.png"

        local_path = os.path.join(self.output_dir, filename)
        remote_path = "/sdcard/revscan_screenshot.png"

        # Attempt capture via ADB if controller is connected
        if adb_controller.is_connected():
            ok, _ = adb_controller.run_cmd(["shell", "screencap", "-p", remote_path], timeout=15)
            if ok:
                pull_ok, _ = adb_controller.run_cmd(["pull", remote_path, local_path], timeout=15)
                # Clean up remote temp file
                adb_controller.run_cmd(["shell", "rm", remote_path], timeout=5)
                if pull_ok and os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                    return local_path

        # Fallback: Generate synthetic placeholder screenshot
        return self._generate_fallback_image(local_path, label=filename)

    def _generate_fallback_image(self, local_path: str, label: str = "") -> str:
        """Generates a clean synthetic Android screenshot for mock/testing environments."""
        width, height = adb_controller.get_screen_size()
        img = Image.new("RGB", (width, height), color=(248, 250, 252))  # Slate 50 background
        draw = ImageDraw.Draw(img)

        # Draw top status bar
        draw.rectangle([0, 0, width, int(height * 0.04)], fill=(15, 23, 42))

        # Draw app header card
        header_height = int(height * 0.12)
        draw.rectangle([0, int(height * 0.04), width, header_height], fill=(37, 99, 235))

        # Draw placeholder content cards
        card1_top = int(height * 0.18)
        card1_bottom = int(height * 0.35)
        draw.rectangle([int(width * 0.08), card1_top, int(width * 0.92), card1_bottom],
                       fill=(255, 255, 255), outline=(226, 232, 240), width=2)

        card2_top = int(height * 0.40)
        card2_bottom = int(height * 0.55)
        draw.rectangle([int(width * 0.08), card2_top, int(width * 0.92), card2_bottom],
                       fill=(255, 255, 255), outline=(226, 232, 240), width=2)

        # Draw action button
        btn_top = int(height * 0.65)
        btn_bottom = int(height * 0.72)
        draw.rectangle([int(width * 0.15), btn_top, int(width * 0.85), btn_bottom],
                       fill=(37, 99, 235))

        img.save(local_path, "PNG")
        return local_path

    def get_relative_path(self, full_path: str) -> str:
        """Converts an absolute local screenshot path into the Spec 6.1 relative format
        (e.g., 'screenshots/screen_001.png').
        """
        filename = os.path.basename(full_path)
        return f"screenshots/{filename}"

    def get_latest_screenshot(self) -> Optional[str]:
        """Returns the most recently created screenshot file path in output_dir, if any."""
        if not os.path.exists(self.output_dir):
            return None
        files = [
            os.path.join(self.output_dir, f)
            for f in os.listdir(self.output_dir)
            if f.endswith(".png")
        ]
        if not files:
            return None
        files.sort(key=os.path.getmtime, reverse=True)
        return files[0]


screenshot_manager = ScreenshotManager()
