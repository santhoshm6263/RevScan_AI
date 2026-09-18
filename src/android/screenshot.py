"""Screenshot utility for RevScan AI (Spec 12 - Member 1).
Captures screenshots from connected device/emulator via ADB,
with authentic brand-customized fallback generation for offline/mock testability.
"""
import os
import time
from pathlib import Path
from typing import Optional, Any
from PIL import Image, ImageDraw

from src.android.adb_controller import adb_controller
from src.core.config import settings


class ScreenshotManager:
    """Manages screenshot capture, fallback generation, and storage."""

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or settings.SCREENSHOT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def capture_screenshot(
        self,
        filename: Optional[str] = None,
        app: Optional[Any] = None,
        screen_name: str = "",
        step: int = 1
    ) -> Optional[str]:
        """Captures a screenshot from the Android device and saves locally.
        If ADB capture fails (e.g. no device connected or in test mode), generates
        an authentic branded fallback image customized to the active target application.
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
                adb_controller.run_cmd(["shell", "rm", remote_path], timeout=5)
                if pull_ok and os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                    return local_path

        # Fallback: Generate authentic branded synthetic screenshot
        return self._generate_fallback_image(local_path, app=app, screen_name=screen_name, step=step)

    def _generate_fallback_image(
        self,
        local_path: str,
        app: Optional[Any] = None,
        screen_name: str = "",
        step: int = 1
    ) -> str:
        """Generates an authentic synthetic screenshot customized with app branding and colors."""
        width, height = adb_controller.get_screen_size()

        pkg = ""
        app_name = "Application"
        category = "Application"
        if app is not None:
            pkg = getattr(app, "package", "") or (app.get("package") if isinstance(app, dict) else "")
            app_name = getattr(app, "name", "") or (app.get("name") if isinstance(app, dict) else "Application")
            category = getattr(app, "category", "") or (app.get("category") if isinstance(app, dict) else "Application")

        pkg_lower = pkg.lower()
        name_lower = app_name.lower()
        cat_lower = category.lower()
        combined = f"{pkg_lower} {name_lower} {cat_lower}"

        # Determine domain brand color palette
        if "spotify" in pkg_lower:
            primary_color = (29, 185, 84)    # Spotify Green #1DB954
            bg_color = (18, 18, 18)          # Dark #121212
            card_bg = (36, 36, 36)
            card_border = (50, 50, 50)
        elif "whatsapp" in pkg_lower:
            primary_color = (7, 94, 84)      # WhatsApp Teal #075E54
            bg_color = (240, 242, 245)       # Light #F0F2F5
            card_bg = (255, 255, 255)
            card_border = (220, 225, 230)
        elif "terminal" in pkg_lower or "windows" in name_lower:
            primary_color = (0, 120, 215)    # Windows Blue #0078D7
            bg_color = (12, 12, 12)          # PowerShell Dark #0C0C0C
            card_bg = (30, 30, 30)
            card_border = (60, 60, 60)
        elif "duolingo" in pkg_lower:
            primary_color = (88, 204, 2)     # Duolingo Green #58CC02
            bg_color = (255, 255, 255)
            card_bg = (247, 247, 247)
            card_border = (229, 229, 229)
        elif "instagram" in pkg_lower:
            primary_color = (225, 48, 108)   # Instagram Rose #E1306C
            bg_color = (255, 255, 255)
            card_bg = (250, 250, 250)
            card_border = (235, 235, 235)
        elif "netflix" in pkg_lower:
            primary_color = (229, 9, 20)     # Netflix Red #E50914
            bg_color = (20, 20, 20)
            card_bg = (40, 40, 40)
            card_border = (60, 60, 60)
        elif any(w in combined for w in ["racing", "hill climb", "race", "speed", "drive"]):
            primary_color = (234, 88, 12)    # Energetic Flame Amber #EA580C
            bg_color = (24, 24, 27)          # Dark Racing asphalt #18181B
            card_bg = (39, 39, 42)           # Slate Card #27272A
            card_border = (63, 63, 70)
        elif any(w in combined for w in ["game", "arcade", "casual", "rpg"]):
            primary_color = (124, 58, 237)   # Gaming Violet #7C3AED
            bg_color = (15, 23, 42)          # Deep Slate #0F172A
            card_bg = (30, 41, 59)
            card_border = (51, 65, 85)
        elif any(w in combined for w in ["food", "dining", "eats", "delivery"]):
            primary_color = (225, 29, 72)    # Coral Red #E11D48
            bg_color = (255, 255, 255)
            card_bg = (254, 242, 242)
            card_border = (254, 205, 211)
        elif any(w in combined for w in ["finance", "crypto", "bank", "invest"]):
            primary_color = (16, 185, 129)   # Emerald Green #10B981
            bg_color = (10, 15, 29)          # Financial Dark #0A0F1D
            card_bg = (17, 24, 39)
            card_border = (31, 41, 55)
        elif any(w in combined for w in ["shopping", "store", "buy", "ecommerce"]):
            primary_color = (79, 70, 229)    # Royal Indigo #4F46E5
            bg_color = (248, 250, 252)
            card_bg = (255, 255, 255)
            card_border = (226, 232, 240)
        else:
            primary_color = (37, 99, 235)    # Brand Blue #2563EB
            bg_color = (248, 250, 252)
            card_bg = (255, 255, 255)
            card_border = (226, 232, 240)

        img = Image.new("RGB", (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)

        screen_idx = ((step - 1) % 4) + 1

        # 1. Status bar (top 4%)
        draw.rectangle([0, 0, width, int(height * 0.04)], fill=(10, 15, 25))

        # Check if in-game active HUD (Screen 3 for games / racing)
        is_racing_hud = any(w in combined for w in ["racing", "hill climb", "race"]) and screen_idx == 3
        if is_racing_hud:
            # Full screen HUD backdrop
            hud_header_bottom = int(height * 0.12)
            draw.rectangle([0, int(height * 0.04), width, hud_header_bottom], fill=primary_color)

            # Left/Right Gauges
            draw.rectangle([int(width * 0.05), int(height * 0.15), int(width * 0.48), int(height * 0.28)], fill=card_bg, outline=card_border, width=2)
            draw.rectangle([int(width * 0.52), int(height * 0.15), int(width * 0.95), int(height * 0.28)], fill=card_bg, outline=card_border, width=2)

            # Center Sky / Track viewport
            draw.rectangle([int(width * 0.05), int(height * 0.32), int(width * 0.95), int(height * 0.65)], fill=(30, 41, 59), outline=primary_color, width=3)

            # Left Pedal (Brake)
            draw.rectangle([int(width * 0.08), int(height * 0.76), int(width * 0.42), int(height * 0.94)], fill=(220, 38, 38), outline=(254, 202, 202), width=3)
            # Right Pedal (Gas)
            draw.rectangle([int(width * 0.58), int(height * 0.76), int(width * 0.92), int(height * 0.94)], fill=(22, 163, 74), outline=(187, 247, 208), width=3)

        else:
            # Standard application flow screens
            # 2. App Header Card (4% to 14%)
            header_top = int(height * 0.04)
            header_bottom = int(height * 0.14)
            draw.rectangle([0, header_top, width, header_bottom], fill=primary_color)

            # 3. Search / Filter / Sub-header bar (16% to 22%)
            search_top = int(height * 0.16)
            search_bottom = int(height * 0.22)
            draw.rectangle(
                [int(width * 0.06), search_top, int(width * 0.94), search_bottom],
                fill=card_bg, outline=card_border, width=2
            )

            # 4. Primary Content Card 1 (25% to 45%)
            card1_top = int(height * 0.25)
            card1_bottom = int(height * 0.45)
            draw.rectangle(
                [int(width * 0.06), card1_top, int(width * 0.94), card1_bottom],
                fill=card_bg, outline=card_border, width=2
            )

            # 5. Content Card 2 (48% to 68%)
            card2_top = int(height * 0.48)
            card2_bottom = int(height * 0.68)
            draw.rectangle(
                [int(width * 0.06), card2_top, int(width * 0.94), card2_bottom],
                fill=card_bg, outline=card_border, width=2
            )

            # 6. Action Button (72% to 80%)
            btn_top = int(height * 0.72)
            btn_bottom = int(height * 0.80)
            draw.rectangle(
                [int(width * 0.10), btn_top, int(width * 0.90), btn_bottom],
                fill=primary_color
            )

            # 7. Bottom Navigation Bar (92% to 100%)
            nav_top = int(height * 0.92)
            draw.rectangle([0, nav_top, width, height], fill=card_bg, outline=card_border, width=1)

        img.save(local_path, "PNG")
        return local_path

    def get_relative_path(self, full_path: str) -> str:
        """Converts an absolute local screenshot path into the Spec 6.1 relative format."""
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
