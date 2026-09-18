"""Design analyzer for extracting basic color palette and theme (Spec 7.0, Spec 12 - Member 3)."""
import os
from typing import Optional, Tuple
from PIL import Image
from src.core.models import DesignInfo


class DesignAnalyzer:
    """Extracts basic design system attributes from screen screenshots."""

    @staticmethod
    def _is_chromatic(r: int, g: int, b: int) -> bool:
        """Determines if a color has sufficient saturation to be considered an accent color."""
        # Filter out pure blacks, pure whites, and near-grays
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        is_too_dark = max_val < 35
        is_too_bright = min_val > 235
        return (diff > 35) and not is_too_dark and not is_too_bright

    @staticmethod
    def _rgb_to_hex(r: int, g: int, b: int) -> str:
        return f"#{r:02X}{g:02X}{b:02X}"

    def analyze(self, screenshot_path: Optional[str] = None) -> DesignInfo:
        """Extracts dominant primary color, background color, and theme from screenshot."""
        default_design = DesignInfo(
            primary_color="#2563EB",
            background_color="#FFFFFF",
            theme="light"
        )

        if not screenshot_path or not os.path.exists(screenshot_path):
            return default_design

        try:
            with Image.open(screenshot_path) as img:
                # Convert to RGB and resize to small thumbnail
                rgb_img = img.convert("RGB").resize((64, 64), Image.Resampling.LANCZOS)

                # Quantize adaptively to 16 dominant colors to guarantee reliable counting
                quantized = rgb_img.convert("P", palette=Image.Palette.ADAPTIVE, colors=16).convert("RGB")
                colors = quantized.getcolors(256)

                if not colors:
                    return default_design

                # Sort by pixel count descending
                sorted_colors = sorted(colors, key=lambda t: t[0], reverse=True)

                # Dominant color is background
                bg_count, bg_rgb = sorted_colors[0]
                bg_r, bg_g, bg_b = bg_rgb[:3]
                bg_hex = self._rgb_to_hex(bg_r, bg_g, bg_b)

                # Calculate background luminance for theme
                lum = 0.299 * bg_r + 0.587 * bg_g + 0.114 * bg_b
                theme = "light" if lum > 128 else "dark"

                # Search for primary accent / brand color among the quantized palette
                primary_hex = "#2563EB"  # default spec primary color
                for count, rgb in sorted_colors:
                    r, g, b = rgb[:3]
                    if self._is_chromatic(r, g, b):
                        primary_hex = self._rgb_to_hex(r, g, b)
                        break

                return DesignInfo(
                    primary_color=primary_hex,
                    background_color=bg_hex,
                    theme=theme
                )
        except Exception as e:
            print(f"[DesignAnalyzer] Error extracting design from '{screenshot_path}': {e}")

        return default_design


design_analyzer = DesignAnalyzer()
