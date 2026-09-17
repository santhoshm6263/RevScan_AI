"""Screen analysis and deduplication (Spec 16, Spec 12 - Member 3).
Calculates screen signatures, infers screen purposes, and handles deduplication.
"""
import hashlib
from typing import List, Optional, Tuple
from src.core.models import ScreenModel, ElementModel


class ScreenAnalyzer:
    """Analyzes and identifies unique screens."""

    def __init__(self):
        self.known_signatures = {}  # signature -> screen_id
        self.screen_counter = 0

    def compute_signature(self, elements: List[ElementModel]) -> str:
        """Computes a normalized structural hash signature for deduplication."""
        tokens = []
        for elem in sorted(elements, key=lambda e: (e.bounds[1], e.bounds[0])):
            tokens.append(f"{elem.type}:{elem.text}:{elem.clickable}")
        raw = "|".join(tokens)
        return hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]

    def infer_name_and_purpose(self, elements: List[ElementModel]) -> Tuple[str, str]:
        """Infers screen name and purpose from constituent elements."""
        texts = [e.text.lower() for e in elements if e.text]
        all_text = " ".join(texts)

        if "login" in all_text or "sign in" in all_text or "password" in all_text:
            return "Login", "User authentication screen"
        elif "sign up" in all_text or "register" in all_text or "create account" in all_text:
            return "Registration", "New user registration screen"
        elif "profile" in all_text or "account" in all_text:
            return "Profile", "User profile and settings"
        elif "cart" in all_text or "checkout" in all_text:
            return "Checkout", "Shopping cart and order checkout"
        elif "search" in all_text:
            return "Search", "Search and filter items"
        elif "home" in all_text or "dashboard" in all_text:
            return "Home", "Main application landing screen"

        return f"Screen_{self.screen_counter + 1:03d}", "Application functional view"

    def analyze_or_get_screen(self, elements: List[ElementModel], screenshot_path: str = "") -> Tuple[ScreenModel, bool]:
        """Returns (screen, is_new). If known, returns existing screen ID."""
        signature = self.compute_signature(elements)
        if signature in self.known_signatures:
            existing_id = self.known_signatures[signature]
            name, purpose = self.infer_name_and_purpose(elements)
            return ScreenModel(
                id=existing_id,
                name=name,
                purpose=purpose,
                screenshot=screenshot_path,
                elements=elements
            ), False

        self.screen_counter += 1
        screen_id = f"screen_{self.screen_counter:03d}"
        self.known_signatures[signature] = screen_id
        name, purpose = self.infer_name_and_purpose(elements)

        screen = ScreenModel(
            id=screen_id,
            name=name,
            purpose=purpose,
            screenshot=screenshot_path,
            elements=elements
        )
        return screen, True


screen_analyzer = ScreenAnalyzer()
