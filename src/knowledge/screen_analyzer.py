"""Screen analysis, deduplication, and classification (Spec 6.1, Spec 12 - Member 3).
Calculates structural signatures, infers screen names & purposes, and manages screen deduplication.
"""
import hashlib
import re
from typing import List, Tuple, Dict, Optional
from src.core.models import ScreenModel, ElementModel


class ScreenAnalyzer:
    """Analyzes and identifies unique screens."""

    def __init__(self):
        self.known_signatures: Dict[str, str] = {}  # signature -> screen_id
        self.known_screens: Dict[str, ScreenModel] = {}  # screen_id -> ScreenModel
        self.screen_counter: int = 0

    def reset(self):
        """Resets the analyzer state for a new scan."""
        self.known_signatures.clear()
        self.known_screens.clear()
        self.screen_counter = 0

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Strips volatile dynamic content (timestamps, numbers, battery) to stabilize signature."""
        t = text.strip().lower()
        # Remove timestamps like 10:45 or 12:30 PM
        t = re.sub(r"\b\d{1,2}:\d{2}(?::\d{2})?(?:\s*[ap]m)?\b", "", t)
        # Remove standalone numbers or percentages like 95% or 100
        t = re.sub(r"\b\d+%\b", "", t)
        t = re.sub(r"\b\d+\b", "", t)
        return t.strip()

    def compute_signature(self, elements: List[ElementModel]) -> str:
        """Computes a normalized structural hash signature for screen deduplication."""
        tokens = []
        # Sort deterministically by top coordinate, then left coordinate
        for elem in sorted(elements, key=lambda e: (e.bounds[1], e.bounds[0], e.id)):
            norm_text = self._normalize_text(elem.text)
            tokens.append(f"{elem.type}:{norm_text}:{elem.clickable}:{elem.input}")
        raw = "|".join(tokens)
        return hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]

    def infer_name_and_purpose(self, elements: List[ElementModel]) -> Tuple[str, str]:
        """Infers screen name and purpose from constituent element types, texts, and IDs."""
        texts = [e.text.lower() for e in elements if e.text]
        ids = [e.id.lower() for e in elements if e.id]
        combined = " ".join(texts + ids)

        # Dialog / Confirmation
        if any(w in combined for w in ["are you sure", "confirm", "permission", "allow", "deny", "dismiss"]):
            return "Confirmation Dialog", "System confirmation or permission dialog"

        # Authentication / Login
        if any(w in combined for w in ["login", "sign in", "sign_in", "password", "username", "authenticate"]):
            return "Login", "User authentication screen"

        # Registration / Sign up
        if any(w in combined for w in ["sign up", "sign_up", "register", "create account", "new account"]):
            return "Registration", "New user registration screen"

        # Onboarding / Intro
        if any(w in combined for w in ["welcome", "get started", "onboarding", "intro", "walkthrough", "tutorial"]):
            return "Onboarding", "Application welcome and onboarding screen"

        # Cart / Checkout
        if any(w in combined for w in ["checkout", "cart", "basket", "place order", "payment", "order summary"]):
            return "Checkout", "Shopping cart and order checkout screen"

        # Item Details / Product
        if any(w in combined for w in ["item detail", "product detail", "specifications", "add to cart", "buy now"]):
            return "Item Details", "Detailed view of selected product or item"

        # Profile / Account
        if any(w in combined for w in ["profile", "account", "my profile", "avatar", "user info", "logout"]):
            return "Profile", "User profile and account settings"

        # Settings
        if any(w in combined for w in ["settings", "preferences", "configuration", "privacy"]):
            return "Settings", "Application settings and configuration screen"

        # Search / Filter
        if any(w in combined for w in ["search", "filter", "query", "find"]):
            return "Search", "Search and filter items"

        # Notifications
        if any(w in combined for w in ["notification", "notifications", "alerts", "inbox", "messages"]):
            return "Notifications", "User notifications and messages screen"

        # Catalog / Feed / List
        if any(w in combined for w in ["catalog", "categories", "category", "feed", "explore", "discover"]):
            return "Catalog", "Browse catalog and category listings"

        # Home / Main
        if any(w in combined for w in ["home", "dashboard", "main", "overview"]):
            return "Home", "Main application landing dashboard"

        return f"Screen_{self.screen_counter + 1:03d}", "Application functional view"

    def analyze_or_get_screen(
        self,
        elements: List[ElementModel],
        screenshot_path: str = ""
    ) -> Tuple[ScreenModel, bool]:
        """Returns (screen, is_new).
        If known, returns existing ScreenModel enriched with newly provided screenshot/actions.
        """
        signature = self.compute_signature(elements)
        if signature in self.known_signatures:
            existing_id = self.known_signatures[signature]
            existing_screen = self.known_screens.get(existing_id)
            if existing_screen:
                # Enrich with screenshot if previously missing
                if not existing_screen.screenshot and screenshot_path:
                    existing_screen.screenshot = screenshot_path
                return existing_screen, False

            name, purpose = self.infer_name_and_purpose(elements)
            screen = ScreenModel(
                id=existing_id,
                name=name,
                purpose=purpose,
                screenshot=screenshot_path,
                elements=elements
            )
            self.known_screens[existing_id] = screen
            return screen, False

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
        self.known_screens[screen_id] = screen
        return screen, True


screen_analyzer = ScreenAnalyzer()
