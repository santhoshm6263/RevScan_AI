"""Design analyzer for extracting basic color palette and theme (Spec 12 - Member 3)."""
import os
from typing import Optional
from PIL import Image
from src.core.models import DesignInfo


class DesignAnalyzer:
    """Extracts basic design system attributes from screen screenshots."""

    def analyze(self, screenshot_path: Optional[str] = None) -> DesignInfo:
        """Extracts dominant colors and theme from screenshot if available."""
        if not screenshot_path or not os.path.exists(screenshot_path):
            return DesignInfo(
                primary_color="#2563EB",
                background_color="#FFFFFF",
                theme="light"
            )

        try:
            with Image.open(screenshot_path) as img:
                img = img.resize((50, 50))
                colors = img.getcolors(50 * 50)
                if colors:
                    sorted_colors = sorted(colors, key=lambda t: t[0], reverse=True)
                    # Use top dominant color as background
                    bg_rgb = sorted_colors[0][1]
                    if isinstance(bg_rgb, tuple) and len(bg_rgb) >= 3:
                        bg_hex = f"#{bg_rgb[0]:02X}{bg_rgb[1]:02X}{bg_rgb[2]:02X}"
                        # Simple luminance check for theme
                        lum = 0.299 * bg_rgb[0] + 0.587 * bg_rgb[1] + 0.114 * bg_rgb[2]
                        theme = "light" if lum > 128 else "dark"
                        return DesignInfo(
                            primary_color="#2563EB",
                            background_color=bg_hex,
                            theme=theme
                        )
        except Exception as e:
            print(f"[DesignAnalyzer] Error extracting design: {e}")

        return DesignInfo(
            primary_color="#2563EB",
            background_color="#FFFFFF",
            theme="light"
        )


design_analyzer = DesignAnalyzer()
